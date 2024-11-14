from django.urls import path
from .api_views import CurrentUserViewSet, branch_list, CalendarEventViewSet

urlpatterns = [
    path('profile/', CurrentUserViewSet.as_view({'get': 'list', 'put': 'update'}), name='profile'),
    path('branches/', branch_list, name='get_branches'),
    path('calendar/events/', CalendarEventViewSet.as_view({'get': 'list', 'post': 'create'}), name='get_add_calendar_events'),
    path('calendar/events/<int:pk>/', CalendarEventViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='update_delete_calendar_events'),
]
