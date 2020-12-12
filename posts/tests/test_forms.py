from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Post, Group, User
from django.test import Client, TestCase


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2 = User.objects.create(
            username='SSS',
            email='ss@mail.ru',
            password='123'
        )
        cls.user = User.objects.create(
            username='VVV',
            email='vv@mail.ru',
            password='123'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=User.objects.first()
        )
        cls.group = Group.objects.create(
            slug='cat',
            title='cat',
            description='Тестовое описание группы'
        )

    def setUp(self):
        self.user = User.objects.get(username='VVV')
        self.user2 = User.objects.get(username='SSS')
        self.group = Group.objects.get(title='cat')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)

    def test_create_post(self):
        '''Валидная форма создает post. Пост появляется в бд.'''
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=False
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        '''При редактировании поста он изменяеся в бд'''
        form_data = {
            'group': Group.objects.get().id,
            'text': 'asd',
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'VVV', 'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.first().text, 'asd')
