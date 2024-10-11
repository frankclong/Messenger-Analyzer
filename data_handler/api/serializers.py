from django.contrib.auth.models import User 
from rest_framework.serializers import ModelSerializer, ValidationError
from ..models import MessagesDataUpload

class MessagesDataUploadSerializer(ModelSerializer):
    class Meta:
        model = MessagesDataUpload
        fields = ['file', 'uploaded_at']

    def validate_file(self, value):
        if not value.name.endswith('.zip'):
            raise ValidationError("Only ZIP files are allowed.")
        return value