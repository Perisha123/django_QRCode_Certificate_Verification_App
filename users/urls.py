# users/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from certificate import views as cert_views
from . import views
from users.views import users_access, users_login, users_register, users_dashboard  # <-- correct name

app_name = "users"

urlpatterns = [
    path('access/', users_access, name='users_access'),
    path('register/', users_register, name='register'),
    path('login/', users_login, name='login'),
    path('dashboard/', views.users_dashboard, name='dashboard'),

    path('user_upload_certificate/', views.user_upload_certificate, name='user_upload_certificate'),


    # User certificate upload
    path('blockchain_certificates/', views.view_certificates_blockchain, name='blockchain_certificates'),

    # QR Scan page for users
    path('scan/', cert_views.qr_scan, name='qr_scan'),

    # Logout and redirect to portal home page
    path('logout/', LogoutView.as_view(next_page='home'), name='users_logout'),
]