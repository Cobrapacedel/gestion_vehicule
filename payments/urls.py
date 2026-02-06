# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # Paiement des amendes
    path("pay-bill/", views.pay_bill_view, name="pay_bill"),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<uuid:pk>/', views.transaction_detail, name='transaction_detail'),
    
    # Transfert
    path('transfer/', views.fund_transfer_list, name='fund_transfer_list'),
    
    path('transfer/new/', views.fund_transfer_create, name='fund_transfer_form'),
    path('transfer/delete/', views.fund_transfer_delete, name='fund_transfer/delete'),

    # Recharge (CBV)
    path("recharges/", views.RechargeListView.as_view(), name="recharge_list"),
    path("recharges/<int:pk>/", views.RechargeDetailView.as_view(), name="recharge_detail"),
    path("recharges/new/", views.RechargeCreateView.as_view(), name="recharge_form"),
    path("recharges/<int:pk>/complete/", views.complete_recharge, name="complete_recharge"),
    
    # Transactions - CRUD
    path("transactions/new/", views.TransactionCreateView.as_view(), name="transaction_create"),
    path("transactions/delete/", views.TransactionDeleteView.as_view(), name="transaction_delete"),

    # Recharge HTMX
    path("htmx/recharge/", views.recharge_create_htmx, name="recharge_htmx_create"),
    path("htmx/recharge-form/", views.recharge_form, name="recharge_form_htmx"),
    
    # Wallet
    path("wallet/", views.wallet_detail, name="wallet_detail"),

    # Paiements (CBV)
    path("payments/", views.PaymentListView.as_view(), name="payment_list"),
    path("payments/<int:pk>/", views.PaymentDetailView.as_view(), name="payment_detail"),
    path("payments/new/", views.PaymentCreateView.as_view(), name="payment_create"),
    path("payments/<int:pk>/edit/", views.PaymentUpdateView.as_view(), name="payment_update"),
    path("payments/<int:pk>/delete/", views.PaymentDeleteView.as_view(), name="payment_delete"),
    
    #path('fine/', views.fine_payment_view, name='fine_payment'),
   # path('toll/', views.toll_payment_view, name='toll_payment'),
    #path('document/', views.document_payment_view, name='document_payment'),
    # Autres URLs...
]

