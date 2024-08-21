from django.urls import path
from .views import HistoricalRecordListView

urlpatterns = [
    path('api/records/', HistoricalRecordListView.as_view(), name='record-list'),
]
