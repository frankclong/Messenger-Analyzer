from django.urls import path
from .views import upload_zip, delete_data

app_name='data_handler'

urlpatterns = [
    path('upload/', upload_zip, name='upload'),
    path('delete/', delete_data, name='delete')
]