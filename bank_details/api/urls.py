from django.urls import path
from bank_details.api.views import (ListBankDetailsView, ListPaymentMethodsView, ListWithdrawMethodsView,
                                    BankAccountDetailsView, BankDetailsView, DeleteBankDetailsView)

urlpatterns = [
    path('payment-methods/', ListPaymentMethodsView.as_view(), name='payment-method-list'),
    path('withdraw-methods/', ListWithdrawMethodsView.as_view(), name='withdraw-method-list'),

    path('bank-details/list/', ListBankDetailsView.as_view(), name='bank-details-list'),
    path('bank-details/save/', BankDetailsView.as_view(), name='add-bank-details'),
    path('bank-account/save/', BankAccountDetailsView.as_view(), name='add-bank-account'),
    path('bank-details/delete/', DeleteBankDetailsView.as_view(), name='delete-bank-details'),
]