from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
