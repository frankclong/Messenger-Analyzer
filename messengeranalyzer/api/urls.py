from django.urls import path, include

urlpatterns = [
    path('', include('core.api.urls'), name='core'),
    path('', include('data_handler.api.urls'), name='data'),
    path('', include('analysis.api.urls'), name='analysis'),
]
