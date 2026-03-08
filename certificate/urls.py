from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "upload/",
        views.upload_certificate,
        name="upload"
    ),

    path(
        "success/",
        views.success,
        name="success"
    ),

    path(
        "verify/<int:cert_id>/",
        views.verify_certificate,
        name="verify"
    ),

]