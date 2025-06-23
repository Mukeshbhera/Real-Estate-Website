from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', views.login, name='login'),
    path('leam_lead_show/<int:id>/', views.teamleader_perticular_leads, name='leam_lead_show'),
    # path('', views.super_dashboard, name='super_dashboard'),
    path('', views.super_admin, name='super_admin'),
    path('admin_add/', views.admin_add, name='admin_add'),
    path('team_dashboard/', views.team_dashboard, name='team_dashboard'),
    path('add_team_leader_user/', views.add_team_leader_user, name='add_team_leader_user'),
    path('team_leader_userss/', views.team_leader_user, name='team_leader_user'),
    # path('home/', views.home, name='home'),
    path('leads/', views.leads, name='leads'),
    path('customer_details/<str:email>/', views.customer_details, name='customer_details'),
    path('assigned/<str:email>/',views.assigned,name='assigned'),
    
    path('view_profile/', views.view_profile, name='view_profile'),
    # path('add_user/', views.add_user, name='add_user'),
    path('lost_leads/', views.lost_leads, name='lost_leads'),
    path('import_leads/', views.import_leads, name='import_leads'),
    path('customer/', views.customer, name='customer'),
    path('maybe/', views.maybe, name='maybe'),
    path('not_picked/', views.not_picked, name='not_picked'),
    path('lost/', views.lost, name='lost'),
    # path('staff/', views.staff, name='staff'),
    # path('new_staff_add/', views.new_staff_add, name='new_staff_add'),
    path('logout/', views.logout_view, name='logout'),
    path('status_update/', views.status_update, name='status_update'),
    path('staff_user/', views.staff_user, name='staff_user'),
    path('all_leads_data/<str:tag>/', views.all_leads_data, name='all_leads_data'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('admin_view_profile/', views.admin_view_profile,name='admin_view_profile'),
    # path('import/', views.import_data, name='import_data'),
    path('excel_upload/', views.excel_upload, name='excel_upload'),
    # path('update_user/', views.update_user, name='update_user'),
    # path('Staff_excel_upload/', views.Staff_excel_upload, name='Staff_excel_upload'),
    path('team_view_profile/', views.team_view_profile, name='team_view_profile'),
    path('staff_view_profile/', views.staff_view_profile, name='staff_view_profile'),
    # path('send-data/', views.send_data, name='send_data'),
    path('adminedit/<int:id>/', views.adminedit, name='editadmin'),
    path('teamedit/<int:id>/', views.teamedit, name='teamedit'),
    path('staffedit/<int:id>/', views.staffedit, name='staffedit'),
    path('bulk_from/', views.bulk_from, name='bulk_from'),
    path('lead/', views.lead, name='lead'),
    path('to-test-data/', views.bulk_from_data, name='bulk_from_data'),
    path('update_send_status/', views.update_send_status, name='update_send_status'),
    path('activitylogs/', views.activitylogs, name='activitylogs'),
    path('edit-marketing/<str:source>/', views.edit_record, name='edit-marketing'),
    path('update-record/', views.update_record, name='update_record'),
    path('export/', views.export_users, name='export_users'),
    # path('customer_details/<int:id>/',views.customer_details,name='customer_details'),

    path('team_leader_staff_interested_leads/<int:id>/', views.team_leader_staff_interested_leads, name='team_leader_staff_interested_leads'),
    
    path('teamcustomer/', views.teamcustomer, name='teamcustomer'),
    path('teamlost_leads/', views.teamlost_leads, name='teamlost_leads'),
    path('teammaybe/', views.teammaybe, name='teammaybe'),
    path('teamnot_picked/', views.teamnot_picked, name='teamnot_picked'),
    path('teamlost/', views.teamlost, name='teamlost'),

    path('lead_user/<int:id>/', views.get_lead_user_data, name='get_lead_user_data'),
    path('lead_user/update/<int:id>/', views.update_lead_user, name='update_lead_user'),

path('project/', views.project, name='project'),

    path('send_file/<int:file_id>/', views.send_file_to_client,
        name='send_file_to_client'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
