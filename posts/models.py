from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст записи',
                            help_text='Введите текст публикации')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Введите название группы')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, null=False,
                            verbose_name='Ссылка группы')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='comments')
    text = models.TextField(
        help_text='Введите текст комментария', verbose_name='Текст', max_length=300)
    created = models.DateTimeField('Дата публикации', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, verbose_name='Подписчик', on_delete=models.SET_NULL,
        related_name='follower', null=True)
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.SET_NULL,
        related_name='following', null=True)
