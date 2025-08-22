from django.urls import path
from .import views

urlpatterns = [
    path('login_page', views.login_page, name='login_page'),  # Login_page
    path('home_page', views.home_view, name='home_page'),
    path('registration_page', views.registration_page, name='registration_page'),  # Registration_page
    path('param_def_list/', views.parameter_definition_list, name='param_def_list'),  # List param_def,
    path('param_def_insert', views.parameter_definition_add, name='param_def_insert'),  # Add param_def
    path('param_def_update/<int:param_def_id>/', views.parameter_definition_add, name='param_def_update'),  # Update param_def
    path('param_def_delete/<int:param_def_id>/', views.parameter_definition_delete, name='param_def_delete'),  # Delete param_def
    path('parameter_definition_search/', views.parameter_definition_search, name='parameter_definition_search'),  # search parameter_definition
    path('parameter_list/', views.parameter_list, name='parameter_list'),  # List parameter,
    path('parameter_insert', views.parameter_add, name='parameter_insert'),  # Add parameter
    path('parameter_update/<int:param_id>/', views.parameter_add, name='parameter_update'),  # Update parameter
    path('parameter_delete/<int:param_id>/', views.parameter_delete, name='parameter_delete'),  # Delete parameter
    path('parameter_search/', views.parameter_search, name='parameter_search'),  # search parameter
    path('project_list/', views.project_list, name='project_list'),  # List project,
    path('project_insert', views.project_add, name='project_insert'),  # Add project
    path('project_update/<int:project_id>/', views.project_add, name='project_update'),  # Update project
    path('project_delete/<int:project_id>/', views.project_delete, name='project_delete'),  # Delete project
    path('project_search/', views.project_search, name='project_search'),  # search project
    path('parameter_definition_lov_insert', views.parameter_definition_lov_add, name='parameter_definition_lov_insert'),  # Add parameter_definition_lov
    path('parameter_definition_lov_update/<int:param_def_lov_id>/', views.parameter_definition_lov_add, name='parameter_definition_lov_update'),  # Add parameter_definition_lov
    path('parameter_definition_lov_list/', views.parameter_definition_lov_list, name='parameter_definition_lov_list'),  # List parameter_definition_lov
    path('parameter_definition_lov_delete/<int:param_def_lov_id>/', views.parameter_definition_lov_delete, name='parameter_definition_lov_delete'),  # Delete parameter_definition_lov_delete
    path('load_lov/', views.load_lov, name='load_lov'),  # load load_lov
    path('parameter_definition_lov_cancel/', views.parameter_definition_lov_cancel, name='parameter_definition_lov_cancel'),  # parameter_definition_lov_cancel
    path('load_units_type/', views.load_units_type, name='load_units_type'),  # load_units_type
    path('load_system_short_name_equipment_name/', views.load_system_short_name_equipment_name, name='load_system_short_name_equipment_name'),  # load_system_short_name_equipment_name
    path('load_equipment_short_name/', views.load_equipment_short_name, name='load_equipment_short_name'),  # load_equipment_short_name
    path('search_keywords', views.search_keywords, name='search_keywords'),
    path('manage_pdfs/', views.manage_pdfs, name='manage_pdfs'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('pdf_compare/', views.pdf_compare_view, name='pdf_compare'),
    path('home_page', views.home_view, name='home_page'),
]