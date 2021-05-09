from django.db.models.query_utils import Q
from apps.Chat.abstract_models import TimeStamp
from django.db import models
from django.conf import settings


class ThreadManager(models.Manager):
    def get_or_create_thread(self, first_user_id, other_user_id):
        first_user_lookup = Q(first_user__id=first_user_id) | Q(
            first_user_id=other_user_id
        )
        second_user_lookup = Q(second_user__id=first_user_id) | Q(
            second_user_id=other_user_id
        )
        thread = Thread.objects.filter(
            first_user_lookup & second_user_lookup
        ).first()
        if not thread:
            thread = Thread.objects.create(
                first_user_id=first_user_id, second_user_id=other_user_id
            )
        return thread


class Thread(TimeStamp):
    first_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_thread_first",
        help_text="User Who Initiate the chat",
    )
    second_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_thread_second",
        help_text="User Who chats with other user",
    )

    objects = ThreadManager()

    @property
    def room_group_name(self):
        return "chat_{}".format(self.id)


class ChatMessage(TimeStamp):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="chat_message",
        help_text="Thread of Chat between them",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="sender",
        on_delete=models.CASCADE,
        related_name="message_user",
    )
    message = models.TextField(blank=False)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.message = self.message.strip()
        self.thread.save()
        super(ChatMessage, self).save(*args, **kwargs)

    def delete_for_all(self):
        self.is_deleted = True
        self.save()
