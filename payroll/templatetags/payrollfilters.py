from django import template

register = template.Library()


@register.filter(name="paid_amount")
def paid_amount(installment):
    paid = [
        deduction.amount for deduction in installment if deduction.installment_payslip()
    ]

    return sum(paid)


@register.filter(name="balance_amount")
def balance_amount(amount, installment):
    balance = amount - paid_amount(installment)
    return balance

@register.filter
def times(number):
    """Generates a range of numbers from 0 to number (exclusive)."""
    return range(number)


@register.filter
def subtract(value, arg):
    """Subtracts arg from value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0  # Default fallback