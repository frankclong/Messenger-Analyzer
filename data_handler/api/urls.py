from django.urls import path, include

from .views import DataUploadView, DataDeleteView

urlpatterns = [
    path("data/upload/", DataUploadView.as_view(), name="upload"),
    path("data/delete/", DataDeleteView.as_view(), name="delete")
]