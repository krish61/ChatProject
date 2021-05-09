import json

from apps.Chat.models import Thread
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
    AsyncWebsocketConsumer,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        other_user = self.scope["url_route"]["kwargs"]["user_to_chat_id"]
        await self.accept()
        self.me = self.scope["user"]
        if self.me.is_anonymous:
            await self.raise_exception("User Doesn't exists with token.")
        self.thread = await self.get_thread(self.me, other_user)
        self.room_name = f"room_{self.thread.id}"
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        raise StopConsumer

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except json.decoder.JSONDecodeError:
            await self.raise_exception("Enter Valid dict")
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def get_thread(self, first_user, other_user_id):
        # Checking both ids
        if first_user.id == int(other_user_id):
            # "Sender Cannot be reciver"
            await self.raise_exception("Sender Cannot be reciver")
        return await self.get_thread_from_db(first_user, other_user_id)

    async def raise_exception(self, message):
        # Send error message and disconnect
        await self.send(text_data=json.dumps({"message": message}))
        await self.close()
        raise StopConsumer

    @database_sync_to_async
    def get_thread_from_db(self, first_user, other_user_id):
        instance = Thread.objects.get_or_create_thread(
            first_user_id=first_user.id, other_user_id=other_user_id
        )
        return instance


class JsonChatConsumer(AsyncJsonWebsocketConsumer):
    async def chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def receive_json(self, content):
        """Content is user send in dict like {"message": "hi"}"""
        data = {"username": self.me.username, **content}
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": data}
        )

    async def connect(self):
        other_user_id = self.scope["url_route"]["kwargs"]["user_to_chat_id"]
        self.me = self.scope["user"]
        self.thread = await self.get_thread(self.me, other_user_id)
        self.room_name = f"room_demo_{self.thread.id}"
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def get_thread(self, first_user, other_user_id):
        # Checking both ids
        if first_user.id == int(other_user_id):
            # "Sender Cannot be reciver"
            self.close()  # Close the connection
            raise StopConsumer
        instance = Thread.objects.get_or_create_thread(
            first_user_id=first_user.id, other_user_id=other_user_id
        )
        return instance
