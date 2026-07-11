from django.urls import path

from . import views

app_name = "reviewer"

urlpatterns = [
    path("", views.create_review, name="create_review"),
]
