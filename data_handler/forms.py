from django import forms
from .models import MessagesDataUpload

class MessagesDataUploadForm(forms.ModelForm):
    class Meta:
        model = MessagesDataUpload
        fields = ['file']