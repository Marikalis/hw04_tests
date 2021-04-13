from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.some_user = User.objects.create_user(username='someuser')
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
        cls.PROFILE = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        cls.GROUP_POSTS = reverse(
            'group_posts',
            kwargs={'slug': cls.group.slug}
        )
        cls.VIEW_POST = reverse(
            'post',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_guests(self):
        """Страницы доступны любому пользователю."""
        url_names = [
            INDEX,
            self.GROUP_POSTS,
            self.PROFILE,
            self.VIEW_POST
        ]
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get(NEW_POST, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_pages_for_authorized_users(self):
        """Страницы доступны авторизованному пользователю."""
        url_names = [
            NEW_POST,
            self.POST_EDIT
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX: 'index.html',
            NEW_POST: 'new_post.html',
            self.GROUP_POSTS: 'group.html',
            self.PROFILE: 'profile.html',
            self.VIEW_POST: 'post.html',
            self.POST_EDIT: 'new_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Шаблон {template}, не соответствует - {url}'
                )
