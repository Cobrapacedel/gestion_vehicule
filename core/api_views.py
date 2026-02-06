from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import DashboardSerializer

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        balance = getattr(user.balance, 'amount', 0)
        vehicles_count = user.vehicles.count()
        notifications_count = user.notifications.filter(is_read=False).count()
        unpaid_fines_count = user.fines.filter(is_paid=False).count()

        data = {
            "balance": balance,
            "vehicles_count": vehicles_count,
            "notifications_count": notifications_count,
            "unpaid_fines_count": unpaid_fines_count,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)
