from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


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
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=User.objects.create_user(username='testuser'),
            group=cls.group_with_post
        )

    def setUp(self):
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='Test_lisa')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'test-slug'})
            ),
            'new_post.html': reverse('new_post'),
        }

        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        posts = response.context['page']
        expected = Post.objects.all()
        self.assertEqual(list(posts), list(expected))

    def test_group_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        group = response.context['group']
        expected_group = PagesTests.group_with_post
        posts = response.context['posts']
        expected_posts = expected_group.posts.all()
        self.assertEqual(list(posts), list(expected_posts))
        self.assertEqual(group, expected_group)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
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

    def test_new_post_with_group_shown_on_index(self):
        # Удостоверимся, что если при создании поста указать группу,
        # то этот пост появляется
        response = self.authorized_client.get(reverse('index'))
        post_text = response.context['page'][0].text
        expected_text = PagesTests.post.text
        self.assertEqual(post_text, expected_text)

    def test_new_post_with_group_doesnt_shown_on_other_group(self):
        # Удостоверимся, что если при создании поста указать группу,
        # то этот пост не появляется в другой группе
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug-empty'})
        )
        posts = response.context['posts']
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
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
