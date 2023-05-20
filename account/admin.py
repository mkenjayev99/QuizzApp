from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name',
                    'last_name', 'is_staff', 'is_superuser',
                    'is_active', 'date_created']
    list_display_links = ['id', 'username', 'first_name']
    list_filter = ['date_created', 'is_staff', 'is_active', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name']
    date_hierarchy = 'date_created'
