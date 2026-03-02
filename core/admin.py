from django.contrib import admin
from .models import News, Event

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'created_at')
    list_filter = ('tag',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_urgent')
    list_filter = ('date', 'is_urgent')