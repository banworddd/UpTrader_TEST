from django import template
from ..models import MenuItem

register = template.Library()


@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    items = MenuItem.objects.filter(
        menu_name=menu_name
    ).select_related('parent').prefetch_related('children')

    def mark_active(items, active_path):
        for item in items:
            item.is_active = (item.get_absolute_url() == active_path)
            if item.children.exists():
                item.has_active_child = mark_active(item.children.all(), active_path)
                item.is_active = item.is_active or item.has_active_child
            else:
                item.has_active_child = False
        return any(item.is_active for item in items)

    mark_active(items, request.path)

    return {
        'items': [item for item in items if item.parent is None],
        'request': request
    }