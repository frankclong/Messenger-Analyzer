from django.db import models

class MessagesDataUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.TextField()
    folder_id = models.TextField()

    def __str__(self):
        return self.name
    

class ConversationMessage(models.Model):
    sender_name = models.TextField()
    content = models.TextField()

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    timestamp_ms = models.BigIntegerField()
    sent_time = models.DateTimeField()
