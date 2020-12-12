from django.test import TestCase
from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Это тестовый текст',
            author=User.objects.create(username='VVV',
                                       email='vv@mail.ru', password='123'),
        )
        cls.group = Group.objects.create(
            title='Cat',
            description='Тестовое описание группы'
        )

    def test_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст записи',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        '''help_text в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Введите название группы',
            'text': 'Введите текст публикации',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_text(self):
        '''text поста совпадает с ожидаемым.'''
        post = PostModelTest.post
        self.assertEquals(str(post), post.text[:15])

    def test_group_name(self):
        '''name группы совпадает с ожидаемым.'''
        group = PostModelTest.group
        self.assertEquals(str(group), group.title)
