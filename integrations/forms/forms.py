from django import forms
from integrations.models import CompanyIntegration
from base.models import Company
from base.services.image_service import FileStorageService


class CompanyIntegrationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        If there is a stored value, show it as ***** but keep the real value in a hidden field
        """
        if self.instance and self.instance.client_secret:
            self.fields['client_secret'].widget.attrs['value'] = '*****'
            self.fields['client_secret'].help_text = 'Leave as ***** to keep the current secret.'

    def clean_client_secret(self):
        data = self.cleaned_data['client_secret']
        if data == '*****' and self.instance and self.instance.client_secret:
            return self.instance.client_secret
        return data

    class Meta:
        model = CompanyIntegration
        fields = [
            'client_id',
            'client_secret',
            'redirect_uri',
            "send_attendance_notifications",
            "send_birthday_notifications",
        ]
        widgets = {
            'client_id': forms.TextInput(
                attrs={"class": "oh-input w-100"}
            ),
           'client_secret': forms.PasswordInput(
               render_value=True,
               attrs={"class": "oh-input w-100"}
            ),
            'redirect_uri': forms.TextInput(
                attrs={"class": "oh-input w-100"}
            ),
            'send_attendance_notifications': forms.CheckboxInput(
                attrs={"class": "oh-checkbox"}
            ),
            'send_birthday_notifications': forms.CheckboxInput(
                attrs={"class": "oh-checkbox"}
            ),

        }
        
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        return super().save(commit)
    
class DocumensoConnectionForm(forms.ModelForm):
    class Meta:
        model = CompanyIntegration
        fields = ['documenso_api_key']
        widgets = {
            'documenso_api_key': forms.TextInput(attrs={"class": "oh-input w-100"}),
        }
        
class WiseConnectionForm(forms.ModelForm):
    class Meta:
        model = CompanyIntegration
        fields = ['wise_api_key']
        widgets = {
            'wise_api_key': forms.TextInput(attrs={"class": "oh-input w-100"}),
        }
        
        