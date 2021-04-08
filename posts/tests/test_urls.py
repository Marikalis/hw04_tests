from django.test import Client, TestCase

from posts.models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            author=User.objects.create_user(username='testuser')
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='MarieL')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new_post.html': '/new/',
        }
        for template, url in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
