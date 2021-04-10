from django.test import Client, TestCase

from posts.models import Group, Post, User
from posts.tests import test_routes


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.some_user = User.objects.create_user(username='someuser')
        # Создаем пользователя
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            author=cls.user
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(URLTests.user)

    def test_pages_for_guests(self):
        """Страницы доступны любому пользователю."""
        url_names = [
            test_routes.INDEX,
            test_routes.RoutesTest.GROUP_POSTS,
            test_routes.RoutesTest.PROFILE,
            test_routes.RoutesTest.VIEW_POST
        ]
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get(test_routes.NEW_POST, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_pages_for_authorized_users(self):
        """Страницы доступны любому пользователю."""
        url_names = [
            test_routes.NEW_POST,
            test_routes.RoutesTest.POST_EDIT
        ]
        for url in url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_edit_not_author(self):
        """Страница редактирования поста недоступна другим пользователям"""
        self.authorized_client.force_login(self.some_user)
        response = self.authorized_client.get('/testuser/1/edit/', follow=True)
        self.assertRedirects(response, '/testuser/1/')
