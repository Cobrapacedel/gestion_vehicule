from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationService:
    """
    Service central de notifications (WebSocket / futur email / SMS)
    """

    @staticmethod
    def send(user, message, extra=None):
        channel_layer = get_channel_layer()

        payload = {
            "type": "send_notification",
            "message": message,
        }

        if extra:
            payload["extra"] = extra

        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            payload
        )

    @staticmethod
    def payment_success(user, amount, currency):
        NotificationService.send(
            user,
            f"✅ Pèman reyisi : {amount} {currency}"
        )

    @staticmethod
    def payment_failed(user, reason=None):
        NotificationService.send(
            user,
            f"❌ Paèman echwe{f' : {reason}' if reason else ''}"
        )

    @staticmethod
    def balance_update(user):
        NotificationService.send(
            user,
            "💰 Mizajou sou balans kont ou"
        )