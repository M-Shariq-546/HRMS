from django.contrib import admin
from .models import CompanyIntegration, AvailableIntegration, DocumensoFieldsData


admin.site.register(CompanyIntegration)
admin.site.register(AvailableIntegration)
admin.site.register(DocumensoFieldsData)
