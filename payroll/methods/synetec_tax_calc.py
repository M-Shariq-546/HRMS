"""
Module: payroll.synetec_tax_calc

This module contains a function for calculating the taxable amount for an employee
based on their contract details and income information for pakistani currency and role of fbr slabs.
"""

import datetime
from horilla.utils.logger import HorillaLogger

from payroll.methods.methods import (
    compute_yearly_taxable_amount,
    convert_year_tax_to_period,
)
from payroll.methods.payslip_calc import (
    calculate_gross_pay,
    calculate_taxable_gross_pay,
)
from payroll.models.models import Contract
from payroll.models.tax_models import TaxBracket

logger = HorillaLogger("payroll.synetec_tax_calc")

def calculate_taxable_amount_pakistan(**kwargs):
    """Calculate FBR Pakistan income tax for a given employee within a period.

    Args:
        employee (int): The ID of the employee.
        start_date (datetime.date): The start date of the period.
        end_date (datetime.date): The end date of the period.
        basic_pay (float): The basic pay amount.

    Returns:
        float: Income tax amount for the specified period.
    """
    employee = kwargs["employee"]
    start_date = kwargs["start_date"]
    end_date = kwargs["end_date"]
    basic_pay = kwargs["basic_pay"]

    contract = Contract.objects.filter(
        employee_id=employee, contract_status="active"
    ).first()

    filing = contract.filing_status
    if not filing:
        return 0
    federal_tax_for_period = 0
    tax_brackets = TaxBracket.objects.filter(filing_status_id=filing).order_by(
        "min_income"
    )
    # Determine number of days in current pay period and full year
    num_days = (end_date - start_date).days + 1
    year = end_date.year
    total_days = (datetime.date(year, 12, 31) - datetime.date(year, 1, 1)).days + 1

    # Get gross income (using preferred calculation)
    calculation_functions = {
        "taxable_gross_pay": calculate_taxable_gross_pay,
        "gross_pay": calculate_gross_pay,
    }
    based = getattr(contract.filing_status, "based_on", "basic_pay")
    if based in calculation_functions:
        income = calculation_functions[based](**kwargs)
        income = float(income[based])
    else:
        income = float(basic_pay)

    # Annualize income for the full year
    # yearly_income = income / num_days * total_days
    yearly_income = income * 12
    yearly_income = round(yearly_income, 2)

    extra_addition_value_to_tax = 0

    '''
    Tax slab and additional value calculation based on annual salary values
    '''

    # Pakistan FBR income tax slabs for salaried individuals (FY 2023–24)
    if filing is not None and not filing.use_py:
        brackets = [
            {
                "rate": int(item["tax_rate"]),
                "min": item["min_income"],
                "max": item["max_income"],
                "base": item['base_amount'],
            }
            for item in tax_brackets.values("tax_rate", "min_income", "max_income", 'base_amount')
        ]
        filterd_brackets = []
        for bracket in brackets:
            if bracket['min'] <= yearly_income <= bracket["max"]:
                bracket["diff"] =  yearly_income - bracket['min']
                bracket["calculated_rate"] = ((int(bracket["rate"]) / 100) * bracket["diff"]) + bracket['base']
                filterd_brackets.append(bracket)
                continue
        federal_tax = sum(bracket["calculated_rate"] for bracket in filterd_brackets)

    elif filing.use_py:
        code = filing.python_code
        code = code.replace("print(", "pass_print(")
        pass_print = """
def pass_print(*args, **kwargs):
    return None
"""
    # Pro-rate annual tax to the current period
    # federal_tax_for_period = (federal_tax / total_days) * num_days
    federal_tax_for_period = federal_tax / 12

    federal_tax_for_period = convert_year_tax_to_period(
        federal_tax_for_period=federal_tax_for_period,
        yearly_tax=federal_tax,
        total_days=total_days,
        start_date=start_date,
        end_date=end_date,
    )
    return round(federal_tax_for_period, 2)