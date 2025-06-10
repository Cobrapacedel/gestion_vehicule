from django.urls import path
from .views import (
    TollListView, TollDetailView,
    TollPaymentListView, TollPaymentCreateView, TollPaymentDeleteView,
    TollTransactionListView, TollTransactionDetailView, TollTransactionDeleteView,
    TollDebtListView, TollDebtDetailView, TollDebtDeleteView
)

app_name = "tolls"

urlpatterns = [
    # Toll
    path('tolls/', TollListView.as_view(), name='toll_list'),
    path('tolls/<int:pk>/', TollDetailView.as_view(), name='toll_detail'),

    # TollPayment
    path('toll/', TollPaymentListView.as_view(), name='toll_payment_list'),
    path('toll/create/', TollPaymentCreateView.as_view(), name='toll_payment_form'),
    path('toll/<int:pk>/delete/', TollPaymentDeleteView.as_view(), name='payment_delete'),

    # TollTransaction
    path('transactions/', TollTransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:pk>/', TollTransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/delete/', TollTransactionDeleteView.as_view(), name='transaction_delete'),

    # TollDebt
    path('debts/', TollDebtListView.as_view(), name='debt_list'),
    path('debts/<int:pk>/', TollDebtDetailView.as_view(), name='debt_detail'),
    path('debts/<int:pk>/delete/', TollDebtDeleteView.as_view(), name='debt_delete'),
]