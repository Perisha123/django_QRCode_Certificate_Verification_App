from django.contrib import admin
from django.urls import path, include
from certificate import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # DJANGO ADMIN PANEL
    path('admin/', admin.site.urls),

    # HOME PAGE
    path('', views.home, name='home'),

    # ADMIN AUTH
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # ADMIN DASHBOARD
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # USER DASHBOARD
    path('users-dashboard/', views.users_dashboard, name='users_dashboard'),

    # CERTIFICATE UPLOAD
    path('upload/', views.upload_certificate, name='upload_certificate'),

    # QR SCAN PAGE
    path('scan/', views.qr_scan, name='qr_scan'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),
   
    # VERIFY CERTIFICATE
    path('verify/<str:file_hash>/', views.verify_certificate, name='qr_verify'),

    # USERS APP
    path('users/', include('users.urls')),
    path('', include('certificate.urls')),  # important: include your app URLs


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)