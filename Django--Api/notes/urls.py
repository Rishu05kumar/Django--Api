# project/urls.py
from django.urls import path
from notes import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('employee/add/', views.add_info, name='add_info'),
    path('employee/edit/<int:emp_id>/', views.edit_employee, name='edit_employee'),
    path('employee/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # API
    path('api/register/', views.register_user),
    path('api/login/', views.login_user),
    path('api/employees/', views.employee_list),
    path('api/employees/<int:emp_id>/', views.employee_detail),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
