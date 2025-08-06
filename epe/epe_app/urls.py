from django.urls import path
from .import views

urlpatterns = [
    path('login_page', views.login_page, name='login_page'),  # Login_page
    path('home_page', views.home_view, name='home_page'),
    path('registration_page', views.registration_page, name='registration_page'),  # Registration_page
    path('param_def_list/', views.parameter_definition_list, name='param_def_list'),  # List country,
    path('param_def_insert', views.parameter_definition_add, name='param_def_insert'),  # Add country
    path('param_def_update/<int:param_def_id>/', views.parameter_definition_add, name='param_def_update'),  # Update country
    path('param_def_delete/<int:param_def_id>/', views.parameter_definition_delete, name='param_def_delete'),  # Delete country
    path('parameter_definition_search/', views.parameter_definition_search, name='parameter_definition_search'),  # Delete country
    path('parameter_list/', views.parameter_list, name='parameter_list'),  # List country,
    path('parameter_insert', views.parameter_add, name='parameter_insert'),  # Add country
    path('parameter_update/<int:param_id>/', views.parameter_add, name='parameter_update'),  # Update country
    path('parameter_delete/<int:param_id>/', views.parameter_delete, name='parameter_delete'),  # Delete country
    path('parameter_search/', views.parameter_search, name='parameter_search'),  # Delete country
    path('project_list/', views.project_list, name='project_list'),  # List country,
    path('project_insert', views.project_add, name='project_insert'),  # Add country
    path('project_update/<int:project_id>/', views.project_add, name='project_update'),  # Update country
    path('project_delete/<int:project_id>/', views.project_delete, name='project_delete'),  # Delete country
    path('project_search/', views.project_search, name='project_search'),  # Delete country
]