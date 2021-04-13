from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')
POST_TEXT = 'Тестовый пост'


class PostFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='MarieL')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text=POST_TEXT,
            author=self.user,
        )
        self.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )
        self.EDIT_POST = reverse(
            'post_edit',
            kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id
            }
        )
        self.POST = reverse(
            'post',
            kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id
            }
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_before = set(Post.objects.all())
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        list_diff = posts_before ^ posts_after
        new_post = list(list_diff)[0]
        self.assertEqual(len(list_diff), 1)
        self.assertTrue(
            new_post.text == POST_TEXT
            and new_post.group == self.group
            and new_post.author == self.user
        )
        self.assertRedirects(response, INDEX)

    def test_post_edit(self):
        """При редактировании поста изменяется запись в базе данных."""
        text_after_edit = 'Тестовый пост после редактирования'
        form_data = {
            'text': text_after_edit,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            self.EDIT_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST)
        post_after_edit = response.context['post']
        self.assertEqual(post_after_edit.text, text_after_edit)
        self.assertEqual(post_after_edit.group, self.group)
        self.assertEqual(post_after_edit.author, self.user)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST)
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
