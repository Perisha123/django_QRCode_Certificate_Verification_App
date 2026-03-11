from django.contrib import admin
from django.urls import path, include
from certificate import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    # HOME
    path('', views.home, name='home'),

    # ADMIN
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.dashboard, name='dashboard'),

    # USER DASHBOARD
    path('dashboard/', views.users_dashboard, name='users_dashboard'),

    # UPLOAD
path('upload/', views.upload_certificate, name='upload_certificate'),  # match template    path('scan/', views.qr_scan, name='qr_scan'),

    # VERIFY
    path('verify/<str:file_hash>/', views.verify_certificate, name='qr_verify'),

    # USERS APP
    path('users/', include('users.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)