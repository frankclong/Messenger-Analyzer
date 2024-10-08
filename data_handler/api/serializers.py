from django.contrib.auth.models import User 
from rest_framework.serializers import ModelSerializer
from ..models import MessagesDataUpload

class MessagesDataUploadSerializer(ModelSerializer):
    class Meta:
        model = MessagesDataUpload
        fields = ['file']