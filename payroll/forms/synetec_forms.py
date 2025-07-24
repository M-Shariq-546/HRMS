from base.forms import Form, ModelForm
from django.forms import TimeInput, Select
from django.template.loader import render_to_string
from django import forms
from pytz import all_timezones
from payroll.models.synetec_models import *
from payroll.methods.time_calculations import generate_am_pm_time_choices

class PayslipAutoGenerateForm(ModelForm):
    class Meta:
        model = PayslipAutomationEmail
        fields = ["scheduler_date", 'scheduler_time', "company", "scheduler_status"]
        labels = {
            "scheduler_time": "Email Scheduler Time",
        }
        widgets = {
            "scheduler_time":Select(choices=generate_am_pm_time_choices(), attrs={"class": "form-control"}),
        }


    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html


class CompanyTimezoneForm(ModelForm):
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in all_timezones],
        label='Timezone',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label='Company',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Company
        fields = [
            'company',
            'timezone'
        ]