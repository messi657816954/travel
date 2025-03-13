from django.urls import path
from transactions.api.views import (TransactionCreateView, TransactionUpdateView, ListUserAccountTransactionsView,
                                    ListUserPendingTransactionsView, ListUserTransactionsView, UserBalanceAccountView)

urlpatterns = [
    path('transaction/save/', TransactionCreateView.as_view(), name='add-transactions'),
    path('transaction/update/', TransactionUpdateView.as_view(), name='update-transaction'),

    path('movement/list/', ListUserAccountTransactionsView.as_view(), name='user-account-movement-list'),
    path('transfer/list/', ListUserTransactionsView.as_view(), name='user-transfer-list'),
    path('pending/list/', ListUserPendingTransactionsView.as_view(), name='user-pending-list'),
    path('balance/', UserBalanceAccountView.as_view(), name='balance-info'),
]