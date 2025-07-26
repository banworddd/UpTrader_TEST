from django.test import TestCase, override_settings
from django.urls import path, reverse
from django.core.exceptions import ValidationError
from .models import MenuItem

# Временные URL для тестов
urlpatterns = [
    path('about/', lambda x: None, name='about'),
    path('contacts/', lambda x: None, name='contacts'),
]


@override_settings(ROOT_URLCONF=__name__)
class MenuItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = MenuItem.objects.create(
            name="Главная",
            url="/",
            menu_name="main_menu",
            order=1
        )
        cls.about = MenuItem.objects.create(
            name="О нас",
            named_url="about",
            menu_name="main_menu",
            parent=cls.home,
            order=2
        )
        cls.external = MenuItem.objects.create(
            name="Документы",
            url="https://example.com/docs",
            menu_name="footer_menu",
            order=1
        )

    def test_model_str(self):
        self.assertEqual(str(self.home), "main_menu: Главная")

    def test_url_validation(self):
        item = MenuItem(
            name="Тест",
            menu_name="main_menu",
            url="/test/",
            named_url="test"
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_get_absolute_url(self):
        self.assertEqual(self.home.get_absolute_url(), "/")
        self.assertEqual(self.about.get_absolute_url(), reverse("about"))
        self.assertEqual(self.external.get_absolute_url(), "https://example.com/docs")

    def test_is_active(self):
        self.assertTrue(self.home.is_active("/"))
        self.assertTrue(self.about.is_active(reverse("about")))

    def test_tree_structure(self):
        self.assertEqual(self.about.parent, self.home)
        self.assertIn(self.about, self.home.children.all())

    def test_has_active_child(self):
        contacts = MenuItem.objects.create(
            name="Контакты",
            url="/contacts/",
            menu_name="main_menu",
            parent=self.about
        )
        self.assertTrue(self.home.has_active_child("/contacts/"))

    def test_ordering(self):
        new_item = MenuItem.objects.create(
            name="Новый",
            url="/new/",
            menu_name="main_menu",
            order=0
        )
        items = MenuItem.objects.filter(menu_name="main_menu").order_by('order')
        self.assertEqual(items.first(), new_item)

    def test_menu_tree_queries(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as queries:
            items = MenuItem.objects.filter(menu_name="main_menu").prefetch_related('children')
            list(items)
        self.assertLessEqual(len(queries), 2)