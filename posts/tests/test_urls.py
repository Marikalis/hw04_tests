from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')
AUTH = '/auth/login'
FAKE_PAGE = '/fake/page'


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
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.some_user)

    def test_pages_codes(self):
        """Страницы доступны любому пользователю."""
        CODE_SUCCESS = 200
        CODE_REDIRECT = 302
        CODE_NOT_FOUND = 404
        USER_GUEST_KEY = 'guest'
        USER_AUTHORIZED_KEY = 'user'
        USER_AUTHORIZED_OTHER_KEY = 'user_other'
        url_names = [
            [USER_GUEST_KEY, INDEX, CODE_SUCCESS],
            [USER_GUEST_KEY, NEW_POST, CODE_REDIRECT],
            [USER_AUTHORIZED_KEY, NEW_POST, CODE_SUCCESS],
            [USER_AUTHORIZED_KEY, self.POST_EDIT, CODE_SUCCESS],
            [USER_AUTHORIZED_OTHER_KEY, self.POST_EDIT, CODE_REDIRECT],
            [USER_GUEST_KEY, self.POST_EDIT, CODE_REDIRECT],
            [USER_GUEST_KEY, self.GROUP_POSTS, CODE_SUCCESS],
            [USER_GUEST_KEY, self.PROFILE, CODE_SUCCESS],
            [USER_GUEST_KEY, self.VIEW_POST, CODE_SUCCESS],
            [USER_GUEST_KEY, FAKE_PAGE, CODE_NOT_FOUND]
        ]
        for user, url, code in url_names:
            with self.subTest():
                if user == USER_GUEST_KEY:
                    response = self.guest_client.get(url)
                elif user == USER_AUTHORIZED_OTHER_KEY:
                    response = self.another_authorized_client.get(url)
                else:
                    response = self.authorized_client.get(url)
                self.assertEqual(
                    code,
                    response.status_code
                )

    def test_redirect(self):
        """Перенаправление пользователя."""
        templates_url_names = [
            ['user', self.POST_EDIT, self.VIEW_POST],
            ['guest', NEW_POST, AUTH + '/?next=' + NEW_POST]
        ]
        for user, url, url_redirect in templates_url_names:
            with self.subTest(url=url):
                if user == 'user':
                    user_page = self.another_authorized_client.get(url)
                else:
                    user_page = self.guest_client.get(url)
                self.assertRedirects(
                    user_page,
                    url_redirect
                )

    def test_edit_not_author(self):
        """Страница редактирования поста недоступна другим пользователям"""
        self.authorized_client.force_login(self.some_user)
        response = self.authorized_client.get(self.POST_EDIT, follow=True)
        self.assertRedirects(response, self.VIEW_POST)

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
