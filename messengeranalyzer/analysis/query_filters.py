from django.db.models import Q

# Django model query filters. Functions return a Q
def valid_message_filter():
    return (~Q(content__iregex="^Reacted.* to your message") 
            & ~Q(content__iregex=".* sent an attachment.")
            & ~Q(content="You can now message and call each other and see info like Active Status and when you've read messages."))