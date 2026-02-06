from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    ContractViewSet,
    ContractListCreateAPIView,
    ContractRetrieveUpdateDeleteAPIView,
    ApplyPenaltyAPIView,
)

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contracts')

urlpatterns = [
    # ------------------------------
    # ROUTES AVEC VIEWSET
    # ------------------------------
    path("", include(router.urls)),  # /api/contracts/

    # ------------------------------
    # ROUTES API CLASSIQUES CONTRACT
    # ------------------------------
    path(
        "contracts-list/",
        ContractListCreateAPIView.as_view(),
        name="api_contract_list"
    ),

    path(
        "contracts/<int:pk>/",
        ContractRetrieveUpdateDeleteAPIView.as_view(),
        name="api_contract_detail"
    ),

    path(
        "contracts/<int:pk>/apply-penalty/",
        ApplyPenaltyAPIView.as_view(),
        name="api_apply_penalty"
    ),
]