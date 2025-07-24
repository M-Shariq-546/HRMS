from threading import Thread
from horilla.utils.logger import HorillaLogger
from base.services.wise_service import WiseService
logger = HorillaLogger('payroll.threadings.wise_thread')
from payroll.models.models import Payslip
from employee.models import Employee
from integrations.models import CompanyIntegration

def WiseThread(request, payslip_id, employee_id, company_instance):
    try:
        payslip = Payslip.objects.get(id=payslip_id)
        employee = Employee.objects.get(id=employee_id.id)
        wise_integration = CompanyIntegration.objects.get(company=company_instance, service_name='wise')
        WiseService.ExecuteWiseTransfer(wise_integration, payslip, employee)
    except Exception as e:
        logger.error(f"Error in WiseThread: {e}")