from django.test import Client, TestCase
from django.urls import reverse

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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            test_routes.INDEX: 'index.html',
            test_routes.NEW_POST: 'new_post.html',
            test_routes.RoutesTest.GROUP_POSTS: 'group.html',
            test_routes.RoutesTest.PROFILE: 'profile.html',
            test_routes.RoutesTest.VIEW_POST: 'post.html',
            reverse(
                'post_edit',
                kwargs={
                    'username': URLTests.post.author.username,
                    'post_id': URLTests.post.id}
            ): 'new_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

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

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get(test_routes.RoutesTest.GROUP_POSTS)
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get(test_routes.NEW_POST, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(test_routes.NEW_POST)
        self.assertEqual(response.status_code, 200)

    def test_edit_not_author(self):
        """Страница редактирования поста недоступна другим пользователям"""
        self.authorized_client.force_login(self.some_user)
        response = self.authorized_client.get('/testuser/1/edit/', follow=True)
        self.assertRedirects(response, '/testuser/1/')
