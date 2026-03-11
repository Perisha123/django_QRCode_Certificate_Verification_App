from django.urls import path
from django.contrib.auth.views import LogoutView
from certificate import views as cert_views
from users.views import users_access, users_login, users_register, users_dashboard

urlpatterns = [
    path('access/', users_access, name='users_access'),   # User portal access page
    path('register/', users_register, name='users_register'),
    path('login/', users_login, name='users_login'),
    path('dashboard/', users_dashboard, name='users_dashboard'),

# QR Scan page for users
    path('scan/', cert_views.qr_scan, name='qr_scan'),
    # Logout and redirect to portal home page
    path('logout/', LogoutView.as_view(next_page='home'), name='users_logout'),
]