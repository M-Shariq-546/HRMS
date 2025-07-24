from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [
    path('start_oauth/<str:service>/', views.start_oauth, name='start_oauth'),
    path('oauth_callback/<str:service>/', views.oauth_callback, name='oauth_callback'),
    path('connect-integration/<str:service>/', views.info_to_connect_integration, name='connect-integration'),
    path('slack-connect-api/', views.slack_connect_api, name='slack_connect_api'),
    path('integrations/<str:service>/disconnect/', views.disconnect_integration, name='disconnect_integration'),
    path('test-disconnect/<str:service>/', views.test_disconnect_api, name='test_disconnect_api'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('integrations_list/', views.integration_list, name='integration_list'),
    path('integrations_react/', views.integration_list_react, name='integration_list_react'),
    path('search-integration/', views.search_integration, name='search-integration'),
    path('slack/callback/', views.slack_callback, name='slack_callback'),
    path('slack/save_channel/', views.save_selected_channel, name='save_selected_channel'),
    path('documenso-templates-fields/', views.documenso_templates_fields, name='documenso_settings'),
    path('wise-recipients/', views.wise_recipients, name='wise_recipients'),
    path('wise-add-recipient/', views.wise_add_recipient, name='wise_add_recipient'),
    path('wise-recent-transfers/', views.wise_recent_transfers, name='wise_transfers'),
    path("save-documenso-mappings/", views.save_documenso_mappings, name="save_documenso_mappings"),
    path("test-api/", views.test_api, name="test_api"),
]
