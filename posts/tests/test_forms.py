from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


class PostFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='MarieL')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост').exists()
        )

    def test_cant_create_post_without_text(self):
        posts_count = Post.objects.count()
        form_data = {'text': ''}
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response, 'form', 'text', 'Обязательное поле.'
        )
        self.assertEqual(response.status_code, 200)

    def test_create_post_edit(self):
        """dsafasfdasdf."""
        text_after_edit = 'Тестовый пост после редактирования'
        form_data = {
            'text': text_after_edit
        }
        self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id
                }
            ),
            data=form_data,
            follow=True
        )

        post_after_edit = Post.objects.filter(pk=self.post.id)[0]
        self.assertEqual(post_after_edit.text, text_after_edit)
