from django.contrib import admin
from django.urls import path
from certificate import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('admin-login/', views.admin_login, name='admin_login'),

    path('admin-logout/', views.admin_logout, name='admin_logout'),

    path('admin-dashboard/', views.dashboard, name='dashboard'),

    path('upload/', views.upload_certificate, name='upload'),

    path('verify/<str:file_hash>/', views.verify_certificate, name='verify'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)