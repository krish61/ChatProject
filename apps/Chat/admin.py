from apps.Chat.models import ChatMessage, Thread
from django.contrib import admin

# Register your models here.
admin.site.register([Thread, ChatMessage])
