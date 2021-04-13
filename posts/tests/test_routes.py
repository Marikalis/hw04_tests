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
        routes_and_urls = [
            [INDEX, '/'],
            [NEW_POST, '/new/'],
            [PROFILE, f'/{user.username}/'],
            [GROUP_POSTS, f'/group/{group.slug}/'],
            [VIEW_POST, f'/{user.username}/{post.id}/'],
            [POST_EDIT, f'/{user.username}/{post.id}/edit/']
        ]
        for route_and_url in routes_and_urls:
            with self.subTest(route_and_url=route_and_url):
                self.assertEqual(route_and_url[0], route_and_url[1])
