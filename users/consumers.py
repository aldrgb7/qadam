import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_user = await self.get_user(self.other_username)
        
        # Создаем уникальную комнату
        user_ids = sorted([self.user.id, self.other_user.id])
        self.room_group_name = f"chat_{user_ids[0]}_{user_ids[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # 🔥 ПОЛЬЗОВАТЕЛЬ ЗАШЕЛ В ЧАТ -> ОН ОНЛАЙН 🔥
        await self.update_user_status(is_online=True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        # 🔥 ПОЛЬЗОВАТЕЛЬ ЗАКРЫЛ ВКЛАДКУ -> СОХРАНЯЕМ ВРЕМЯ 🔥
        if self.user.is_authenticated:
            await self.update_user_status(is_online=False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']

        msg = await self.save_message(message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.user.username,
                'time': msg.created_at.strftime("%H:%M")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'time': event['time']
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, text):
        return Message.objects.create(sender=self.user, receiver=self.other_user, text=text)
    
    
    # 🔥 ФУНКЦИЯ ДЛЯ ОБНОВЛЕНИЯ СТАТУСА 🔥
    @database_sync_to_async
    def update_user_status(self, is_online):
        self.user.is_online = is_online
        if not is_online:
            self.user.last_seen = timezone.now()
        self.user.save()