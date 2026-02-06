from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]
        print("🔥 WEBSOCKET CONNECT – USER =", user)

        if user.is_anonymous:
            print("❌ UTILISATEUR ANONYME → WS REFUSÉ")
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "title": event["title"],
            "message": event["message"],
        }))