# users/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from certificate import views as cert_views
from . import views
from django.contrib.auth import views as auth_views

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

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',      # Form page
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url='/users/password-reset/done/'       # After submitting email
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/users/reset/done/'               # After changing password
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]