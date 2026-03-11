from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.dashboard, name='dashboard'),
    
    # Upload certificate
    path('upload/', views.upload_certificate, name='upload_certificate'),  # matches template

    # Verify certificate
    path('verify/<str:file_hash>/', views.verify_certificate, name='qr_verify'),  # matches template

    # QR scan (if you have this view)
    path('scan/', views.qr_scan, name='qr_scan'),

    # Certificate download (if you have this view)
    path('download/<int:cert_id>/', views.certificate_download, name='certificate_download'),

    # User logout
    path('logout/', views.users_logout, name='logout'),
]