# payments/api_urls.py

from rest_framework.routers import DefaultRouter
from .viewset import RechargeViewSet, TransactionViewSet, PaymentViewSet, BalanceViewSet

router = DefaultRouter()
router.register(r"recharges", RechargeViewSet, basename="recharge")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"balance", BalanceViewSet, basename="balance")

urlpatterns = router.urls