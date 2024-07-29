from django.contrib import admin
from .models import Contact, ConversationMessage

admin.site.register(Contact)
admin.site.register(ConversationMessage)