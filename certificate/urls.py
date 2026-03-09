from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_certificate, name='upload'),

    # Verification
    path('verify/<str:hash>/', views.verify_certificate, name='verify'),
]