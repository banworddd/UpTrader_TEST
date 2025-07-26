from django.db import models
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ValidationError
from django.db.models import Prefetch


class MenuItem(models.Model):
    """
    Модель для пункта меню с поддержкой:
    - Древовидной структуры
    - Named URLs
    - Разных меню на одном сайте
    - Автоматического определения активного пункта
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название пункта",
        help_text="Отображаемый текст меню"
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Родительский пункт",
    )

    url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Прямой URL",
    )

    named_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Именованный URL",
    )

    menu_name = models.CharField(
        max_length=50,
        verbose_name="Системное имя меню",
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ['order', 'name']
        unique_together = [('menu_name', 'name')]
        indexes = [
            models.Index(fields=['menu_name']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.menu_name}: {self.name}"

    def clean(self):
        if not self.url and not self.named_url:
            raise ValidationError("Укажите либо прямой URL, либо именованный")
        if self.url and self.named_url:
            raise ValidationError("Используйте только один тип URL")

    def get_absolute_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.url or '/'
        return self.url or '/'

    def is_active(self, current_path):
        return self.get_absolute_url() == current_path

    def has_active_child(self, current_path, max_depth=3):
        if max_depth <= 0:
            return False
        return any(
            child.is_active(current_path) or
            child.has_active_child(current_path, max_depth - 1)
            for child in self.children.all()
        )

    @classmethod
    def get_menu_tree(cls, menu_name):
        top_level_items = cls.objects.filter(
            menu_name=menu_name,
            parent__isnull=True
        ).prefetch_related(
            Prefetch('children',
                     queryset=cls.objects.all().select_related('parent')
                     )
        ).order_by('order', 'name')

        return top_level_items