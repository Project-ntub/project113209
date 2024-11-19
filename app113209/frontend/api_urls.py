from django.urls import path
from .api_views import CurrentUserViewSet, branch_list, CalendarEventViewSet

urlpatterns = [
    path('profile/', CurrentUserViewSet.as_view({'get': 'list', 'put': 'update'}), name='profile'),
    path('branches/', branch_list, name='get_branches'),
    path('calendar/events/', CalendarEventViewSet.as_view({'post': 'create'}), name='add_calendar_event'),  # 只保留新增事件


]
