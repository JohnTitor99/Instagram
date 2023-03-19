import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from .models import Chat


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        chats = list(Chat.objects.values())

        self.send(text_data=json.dumps({
            'type':'messages',
            'message':chats
        }, default=str))


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        try:
            delMessage = text_data_json['delMessage'] # message id for deleting
            mes = Chat.objects.get(id=delMessage)
            mes.delete()
        except:
            message = text_data_json['message']
            request_user_id = text_data_json['request_user']
            chat_user_id = text_data_json['chat_user']

            request_user = User.objects.get(id=request_user_id)
            chat_user = User.objects.get(id=chat_user_id)

            chat = Chat()
            chat.text=message
            chat.user=request_user
            chat.user2=chat_user

            # save if messageis not empty
            if message != '':
                chat.save()

            # display message if not empty
            if message != '':
                chats = list(Chat.objects.values())
                message = [chats[-1]]   

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message
                    }
                )     


    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'messages',
            'message':message
        }, default=str))