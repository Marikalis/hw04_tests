from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Введите описание группы',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.text[:15]}'

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        unique=True
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
