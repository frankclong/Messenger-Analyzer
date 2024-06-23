from django.urls import path
from .views import upload_zip

app_name='data_handler'

urlpatterns = [
    path('upload/', upload_zip, name='upload'),
]