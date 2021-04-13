from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


INDEX = reverse('index')
NEW_POST = reverse('new_post')


class RoutesTest(TestCase):
    @classmethod
    def test_routes(self):
        self.user = User.objects.create_user(username='testuser')
        self.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )
        self.post = Post.objects.create(
            text='Тестовый пост',
            group=self.group,
            author=self.user
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.PROFILE = reverse(
            'profile',
            kwargs={'username': self.user.username}
        )
        self.GROUP_POSTS = reverse(
            'group_posts',
            kwargs={'slug': self.group.slug}
        )
        self.VIEW_POST = reverse(
            'post',
            kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id}
        )
        self.POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id}
        )
        self.assertEqual(INDEX, '/')
        self.assertEqual(NEW_POST, '/new/')
        self.assertEqual(self.PROFILE, '/testuser/')
        self.assertEqual(self.GROUP_POSTS, '/group/test-slug/')
        self.assertEqual(self.VIEW_POST, '/testuser/1/')
        self.assertEqual(self.POST_EDIT, '/testuser/1/edit/')
