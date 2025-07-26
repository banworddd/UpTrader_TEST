from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_name', 'parent', 'url', 'named_url', 'order')
    list_filter = ('menu_name',)
    search_fields = ('name', 'url')
    list_editable = ('order',)
    fieldsets = (
        (None, {
            'fields': ('name', 'menu_name', 'order')
        }),
        ('Ссылки', {
            'fields': ('url', 'named_url'),
            'description': 'Укажите ТОЛЬКО один вариант'
        }),
        ('Иерархия', {
            'fields': ('parent',),
            'classes': ('collapse',)
        })
    )