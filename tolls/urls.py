from django.urls import path
from .views import (
    TollListView, TollDetailView,
    TollDebtListView, TollDebtDetailView, TollDebtDeleteView, tollbooth_list_view, toll_detail_view   
)
from . import views

app_name = "tolls"

urlpatterns = [
    # Toll
    path('tolls/', TollListView.as_view(), name='toll_list'),
    path('tolls/<int:pk>/', TollDetailView.as_view(), name='toll_detail'),

    # TollDebt
    path('debts/', TollDebtListView.as_view(), name='debt_list'),
    path('debts/<int:pk>/', TollDebtDetailView.as_view(), name='debt_detail'),
    path('debts/<int:pk>/delete/', TollDebtDeleteView.as_view(), name='debt_delete'),
    
    # HTML CLASSIQUE VIEWS PEYAJ
    path('toll/<int:toll_id>pay/', views.toll_pay, name='toll_payment_form'),
    path('tolls/list/', tollbooth_list_view, name='tollbooth_list'),
    path('tolls/<int:toll_id>/detail/', toll_detail_view, name='toll_detail'),
]