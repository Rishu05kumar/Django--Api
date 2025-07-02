from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/register/', views.register_user, name='api_register'),
    path('api/login/', views.login_user, name='api_login'),
    path('api/employees/', views.employee_list, name='api_employees'),
    path('api/employees/<int:emp_id>/', views.employee_detail, name='api_employee_detail'),

    # Web frontend views
    path('home/', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
