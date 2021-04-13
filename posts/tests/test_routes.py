from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


INDEX = reverse('index')
NEW_POST = reverse('new_post')


class RoutesTest(TestCase):
    def test_routes(self):
        user = User.objects.create_user(username='testuser')
        group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )
        post = Post.objects.create(
            text='Тестовый пост',
            group=group,
            author=user
        )
        authorized_client = Client()
        authorized_client.force_login(user)
        PROFILE = reverse(
            'profile',
            kwargs={'username': user.username}
        )
        GROUP_POSTS = reverse(
            'group_posts',
            kwargs={'slug': group.slug}
        )
        VIEW_POST = reverse(
            'post',
            kwargs={
                'username': post.author.username,
                'post_id': post.id}
        )
        POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': post.author.username,
                'post_id': post.id}
        )
        self.assertEqual(INDEX, '/')
        self.assertEqual(NEW_POST, '/new/')
        self.assertEqual(PROFILE, f'/{user.username}/')
        self.assertEqual(GROUP_POSTS, f'/group/{group.slug}/')
        self.assertEqual(VIEW_POST, f'/{user.username}/{post.id}/')
        self.assertEqual(POST_EDIT, f'/{user.username}/{post.id}/edit/')
