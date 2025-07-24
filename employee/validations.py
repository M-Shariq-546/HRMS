def required_fields_check(request, employee):
    if employee.employee_work_info.company_id is None:
        return False, "Add Company Details in Employee Work Profile"
    if employee.employee_work_info.job_position_id is None:
        return False, "Add Job Position Details in Employee Work Profile"
    if employee.get_email() is None:
        return False, "Please Add Work Email to this Employee in Employee Profile"
    if employee.get_full_name() is None:
        return False, "Employee Full Name is missing Please Add in Employee Profile"
    
    return True , 'pass'
    
    
def required_fields_check_candidate(request, candidate):
    if candidate.get_company is None:
        return False, "Company Details are missing in Candidate Profile"
    if candidate.get_job_position is None:
        return False, "Job Position Details are Missing in Candidate Profile"
    if candidate.get_email is None:
        return False, "Candidate Email is required"
    
    return True, 'pass'