from django.urls import path
from . import views
# Instead of importing from certificate.views
# from certificate.views import view_certificate
from users.views import view_certificate  # <-- import from users.views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Admin routes
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upload/', views.upload_certificate, name='upload'),  # admin upload
    path('upload_certificate/edit/<int:pk>/', views.edit_certificate, name='edit_certificate'),
    path('upload_certificate/delete/<int:pk>/', views.delete_certificate, name='delete_certificate'),

    # User routes
    path('users_dashboard/', views.users_dashboard, name='users_dashboard'),
    path('user_upload/', views.user_upload_certificate, name='user_upload_certificate'),

    # Verify certificate
    path('verify/<str:file_hash>/', views.verify_certificate, name='qr_verify'),


    # Certificate download
    path('download/<int:cert_id>/', views.certificate_download, name='certificate_download'),

    # User logout
    path('logout/', views.users_logout, name='logout'),
    path('view/<int:pk>/', view_certificate, name='view_certificate'),

    # QR scan
    path('scan/', views.qr_scan, name='qr_scan'),
]
 