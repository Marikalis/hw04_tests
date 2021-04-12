from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests import test_routes


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_with_post = Group.objects.create(
            title='Группа с постом',
            description='Описание',
            slug='test-slug'
        )
        cls.group_without_post = Group.objects.create(
            title='Группа без поста',
            description='Тестовое описание',
            slug='test-slug-empty'
        )
        cls.user = User.objects.create_user(username='Test_lisa')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group_with_post
        )
        cls.PROFILE = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        cls.GROUP_WITH_POSTS = reverse(
            'group_posts',
            kwargs={'slug': cls.group_with_post.slug}
        )
        cls.GROUP_WITHOUT_POSTS = reverse(
            'group_posts',
            kwargs={'slug': cls.group_without_post.slug}
        )
        cls.VIEW_POST = reverse(
            'post',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id
            }
        )
        cls.POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id
            }
        )

    def setUp(self):
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PagesTests.user)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(test_routes.INDEX)
        posts = response.context['page']
        expected = Post.objects.all()
        self.assertEqual(list(posts), list(expected))

    def test_group_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            PagesTests.GROUP_WITH_POSTS
        )
        group = response.context['group']
        expected_group = PagesTests.group_with_post
        posts = response.context['page']
        expected_posts = expected_group.posts.all()
        self.assertEqual(list(posts), list(expected_posts))
        self.assertEqual(group, expected_group)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(test_routes.NEW_POST)
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        """Словарь context, для страницы редактирования поста
        соответствует."""
        response = self.authorized_client.get(
            PagesTests.POST_EDIT
        )
        posts = Post.objects.filter(pk=self.post.id)
        context = {
            self.post.text: response.context['form'].initial['text'],
            self.group_with_post.title: posts[0].group.title
        }
        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_profile_correct_context(self):
        """Словарь context, для страницы профайла пользователя
        соответствует."""
        response = self.authorized_client.get(
            PagesTests.PROFILE
        )
        user = response.context['user']
        expected_user = PagesTests.user
        posts = response.context['page']
        expected_posts = expected_user.posts.all()[:10]
        self.assertEqual(list(posts), list(expected_posts))
        self.assertEqual(user, expected_user)

    def test_post_view_correct_context(self):
        """Словарь context, для страницы отдкльного поста
        соответствует."""
        response = self.authorized_client.get(
            PagesTests.VIEW_POST
        )
        author = response.context['author']
        expected_author = self.post.author
        post = response.context['post']
        expected_post = self.post
        self.assertEqual(author, expected_author)
        self.assertEqual(post, expected_post)

    def test_new_post_with_group_shown_on_index(self):
        # Удостоверимся, что если при создании поста указать группу,
        # то этот пост появляется
        response = self.authorized_client.get(test_routes.INDEX)
        post_text = response.context['page'][0].text
        expected_text = PagesTests.post.text
        self.assertEqual(post_text, expected_text)

    def test_new_post_with_group_doesnt_shown_on_other_group(self):
        # Удостоверимся, что если при создании поста указать группу,
        # то этот пост не появляется в другой группе
        response = self.authorized_client.get(
            PagesTests.GROUP_WITHOUT_POSTS
        )
        posts = response.context['page']
        self.assertEqual(len(posts), 0)


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        for index in range(13):
            note = f"запись номер {index} "
            Post.objects.create(
                text=note,
                author=user
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        response = self.client.get(test_routes.INDEX)
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(test_routes.INDEX + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
