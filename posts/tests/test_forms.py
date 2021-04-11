from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User
from posts.tests import test_routes


class PostFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='MarieL')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )

        self.EDIT_POST = reverse(
            'post_edit',
            kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id
            }
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост'
        }
        response = self.authorized_client.post(
            test_routes.NEW_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, test_routes.INDEX)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост').exists()
        )

    def test_cant_create_post_without_text(self):
        posts_count = Post.objects.count()
        form_data = {'text': ''}
        response = self.authorized_client.post(
            test_routes.NEW_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response, 'form', 'text', 'Обязательное поле.'
        )
        self.assertEqual(response.status_code, 200)

    def test_create_post_edit(self):
        """При редактировании поста изменяется запись в базе данных."""
        text_after_edit = 'Тестовый пост после редактирования'
        form_data = {
            'text': text_after_edit
        }
        self.authorized_client.post(
            self.EDIT_POST,
            data=form_data,
            follow=True
        )

        post_after_edit = Post.objects.filter(pk=self.post.id)[0]
        self.assertEqual(post_after_edit.text, text_after_edit)
