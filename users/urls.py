# users/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from certificate import views as cert_views
from . import views
from users.views import users_access, users_login, users_register, users_dashboard, upload_certificate  # <-- correct name

urlpatterns = [
    path('access/', users_access, name='users_access'),
    path('register/', users_register, name='users_register'),
    path('login/', users_login, name='users_login'),
    path('dashboard/', views.users_dashboard, name='users_dashboard'),

    # User certificate upload
    path('upload-certificate/', upload_certificate, name='user_upload_certificate'),  # <-- use the URL name you want
    path('blockchain-certificates/', views.view_certificates_blockchain, name='blockchain_certificates'),

    # QR Scan page for users
    path('scan/', cert_views.qr_scan, name='qr_scan'),

    # Logout and redirect to portal home page
    path('logout/', LogoutView.as_view(next_page='home'), name='users_logout'),
]