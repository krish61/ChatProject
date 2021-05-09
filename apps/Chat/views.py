from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.


class SendMessage(APIView):
    """Sends Message to Socket Group.

    Request data be like
    {"group_name":"chat_room_1",
    "message":{"username": "admin",
                        "message":"hello"}}"""

    def post(self, request):
        room_group_name = request.data.get("group_name")
        message = request.data.get("message")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name, {"type": "chat_message", "message": message}
        )
        return Response("message is sent")
