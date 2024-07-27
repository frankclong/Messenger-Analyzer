from django.db import models
from django.contrib.auth.models import User

class MessagesDataUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    folder_id = models.TextField(unique=True)

    def __str__(self):
        return self.name
    

class ConversationMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender_name = models.TextField()
    content = models.TextField()

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    timestamp_ms = models.BigIntegerField()
    sent_time = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'contact', 'content', 'sender_name', 'timestamp_ms')
