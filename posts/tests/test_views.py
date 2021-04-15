from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.settings import PAGE_SIZE

INDEX = reverse('index')
NEW_POST = reverse('new_post')
DESCRIPTION = 'Тестовое описание'
USERNAME = 'Test_lisa'
GROUP_WITHOUT_POST_SLAG = 'test-slug-empty'
GROUP_WITH_POST_SLAG = 'test-slug'
PROFILE = reverse(
    'profile',
    kwargs={'username': USERNAME}
)
GROUP_WITH_POSTS = reverse(
    'group_posts',
    kwargs={'slug': GROUP_WITH_POST_SLAG}
)
GROUP_WITHOUT_POSTS = reverse(
    'group_posts',
    kwargs={'slug': GROUP_WITHOUT_POST_SLAG}
)


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_with_post = Group.objects.create(
            title='Группа с постом',
            description=DESCRIPTION,
            slug=GROUP_WITH_POST_SLAG
        )
        cls.group_without_post = Group.objects.create(
            title='Группа без поста',
            description=DESCRIPTION,
            slug=GROUP_WITHOUT_POST_SLAG
        )
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group_with_post
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        posts = self.authorized_client.get(INDEX).context['page']
        first_post = posts[0]
        self.assertEqual(len(posts), 1)
        self.assertEqual(first_post.text, self.post.text)
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)

    def test_group_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            GROUP_WITH_POSTS
        )
        group = response.context['group']
        expected_group = self.group_with_post
        posts = response.context['page']
        expected_posts = expected_group.posts.all()
        self.assertEqual(list(posts), list(expected_posts))
        self.assertEqual(group, expected_group)

    def test_profile_correct_context(self):
        """Словарь context, для страницы профайла пользователя
        соответствует."""
        response = self.authorized_client.get(
            PROFILE
        )
        expected_user = self.user
        posts = response.context['page']
        expected_posts = expected_user.posts.all()[:PAGE_SIZE]
        self.assertEqual(list(posts), list(expected_posts))

    def test_post_view_correct_context(self):
        """Словарь context, для страницы отдкльного поста
        соответствует."""
        response = self.authorized_client.get(
            self.VIEW_POST
        )
        author = response.context['author']
        expected_author = self.post.author
        post = response.context['post']
        expected_post = self.post
        self.assertEqual(author, expected_author)
        self.assertEqual(post, expected_post)

    def test_new_post_with_group_doesnt_shown_on_other_group(self):
        response = self.authorized_client.get(
            GROUP_WITHOUT_POSTS
        )
        posts = response.context['page']
        self.assertFalse(self.post in posts)


class PaginatorViewsTest(TestCase):
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
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        response = self.client.get(INDEX)
        self.assertEqual(
            len(response.context.get('page').object_list),
            PAGE_SIZE
        )

    def test_second_page_containse_three_records(self):
        response = self.client.get(INDEX + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
