import datetime as dt
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


INDEX = reverse('index')
NEW_POST = reverse('new_post')


class RoutesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
            pub_date=dt.datetime.today()
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_routes(self):
        self.assertEqual(INDEX, '/')
        self.assertEqual(NEW_POST, '/new/')
        self.assertEqual(self.PROFILE, '/testuser/')
        self.assertEqual(self.GROUP_POSTS, '/group/test-slug/')
        self.assertEqual(self.VIEW_POST, '/testuser/1/')
        self.assertEqual(self.POST_EDIT, '/testuser/1/edit/')
