# admin.py
from django.contrib import admin
from .models import ActionLog

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'timestamp', 'details')
    search_fields = ('user__username', 'action_type', 'details')
