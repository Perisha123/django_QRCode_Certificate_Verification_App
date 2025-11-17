from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_document, name="upload"),
    path('verify/', views.verify_document, name="verify"),
]
