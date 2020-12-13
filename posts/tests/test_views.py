from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Comment, Group, Post, User, Follow
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='VVV',
            email='vv@mail.ru',
            password='123',
        )
        cls.user2 = User.objects.create(
            username='SSS',
            email='ss@mail.ru',
            password='123',
        )
        cls.user3 = User.objects.create(
            username='AAA',
            email='aa@mail.ru',
            password='123',
        )
        cls.group = Group.objects.create(
            title='cat',
            slug='cat',
            description='Test description',
        )
        cls.group = Group.objects.create(
            title='dog',
            slug='dog',
            description='Test description',
        )
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        for i in range(15):
            Post.objects.create(
                text='Текст',
                author=User.objects.get(username='VVV'),
                group=Group.objects.get(title='cat'),
                image=image,
            )
        cls.post = Post.objects.first()

    def setUp(self):
        self.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about me',
            content='<b>content</b>'
        )
        self.flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<b>content</b>'
        )
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.image = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        site = Site.objects.get(pk=1)
        self.flat_about.sites.add(site)
        self.flat_tech.sites.add(site)
        self.static_pages = ('/about-author/', '/about-spec/')
        self.guest_client = Client()
        self.user2 = User.objects.get(username='SSS')
        self.user3 = User.objects.get(username='AAA')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user3)
        self.user = User.objects.get(username='VVV')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        cache.clear()
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': 'cat'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Тест загрузки картинки
    def test_index_page_and_post_group_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом. Новый пост
        появляется на главной странице. Паджинатор помещает правильное кол-во
        постов. Картинка передаётся в context.'''
        cache.clear()
        image = self.image
        response = self.authorized_client.get(reverse('index'))
        post = response.context['page'][0]
        self.assertEqual(post.text, 'Текст')
        self.assertEqual(post.group.title, 'cat')
        self.assertEqual(post.image.size, image.size)
        self.assertEqual(post.author, self.user)
        self.assertEqual(len(response.context['page']), 10)

    # Тест загрузки картинки
    def test_group_pages_show_correct_context(self):
        '''Шаблон group сформирован с правильным контекстом. Новый пост
        появляется на странице выбранной группы. Картинка отображается в группе'''
        image = self.image
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'cat'})
        )
        post = response.context['page'][0]
        self.assertEqual(post.image.size, image.size)
        self.assertEqual(response.context.get('group').title, 'cat')
        self.assertEqual(response.context.get('group').description,
                         'Test description')
        self.assertEqual(response.context.get('group').slug, 'cat'),
        self.assertEqual(response.context.get('posts')[0].text, 'Текст'),

    def test_new_post_pages_show_correct_context(self):
        '''Шаблон new_post сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_post_correct_show(self):
        '''Шаблон group сформирован с правильным контекстом. Новый пост не
        появляется в другой группе'''
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'dog'})
        )
        self.assertFalse(response.context.get('posts'))

    def test_profile_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        image = self.image
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'VVV'})
        )
        post = response.context['page'][0]
        self.assertEqual(post.image.size, image.size)
        self.assertEqual(response.context.get('post')[0].text, 'Текст')
        self.assertEqual(response.context.get('profile').username, 'VVV')

    def test_post_edit_correct_context(self):
        '''Шаблон /<username>/<post_id>/edit/ сформирован с правильным
        контекстом.'''
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': 'VVV', 'post_id': '1'})
        )
        post_text_0 = response.context.get('post').text
        profile_0 = response.context.get('profile').username
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(profile_0, 'VVV')

    def test_post_correct_context(self):
        '''Шаблон /<username>/<post_id>/ сформирован с правильным контекстом
        '''
        image = self.image
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'VVV', 'post_id': '1'})
        )
        post = response.context.get('post').image
        self.assertEqual(post.size, image.size)
        self.assertEqual(response.context.get('post').text, 'Текст')
        self.assertEqual(response.context.get('profile').username, 'VVV')

    def test_flatpages_about_author_correct_context(self):
        '''Шаблон /<flatpages>/ сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('about-author'))
        title_0 = response.context.get('flatpage').title
        self.assertEqual(title_0, 'about me')

    def test_flatpages_about_tech_correct_context(self):
        '''Шаблон /<flatpages>/ сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('about-spec'))
        title_0 = response.context.get('flatpage').title
        self.assertEqual(title_0, 'about my tech')

    def test_index_cache(self):
        '''Index правильно кэширует данные'''
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        old = response.context.get('page').count
        Post.objects.create(
            text='Текст',
            author=User.objects.get(username='VVV'),
        )
        new = response.context.get('page').count
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        after = response.context.get('page').count
        self.assertEqual(old, new)
        self.assertNotEqual(new, after)

    def test_follow(self):
        '''Авторизованный пользователь может подписываться на других
        пользователей'''
        count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': 'SSS'}))
        follow = Follow.objects.filter(
            user=self.user,
            author=self.user2).exists()
        self.assertEqual(count + 1, Follow.objects.count())
        self.assertTrue(follow)

    def test_unfollow(self):
        '''Авторизованный пользователь может отпсываться от других
        пользователей'''
        Follow.objects.create(user=self.user, author=self.user2)
        count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={'username': 'SSS'}))
        self.assertEqual(count - 1, Follow.objects.count())

    def test_new_post_in_follow(self):
        '''Новая запись появляется у подписанных пользователей и не появляется у не подписаных'''
        Follow.objects.create(user=self.user, author=self.user2)
        Post.objects.create(
            text='Текст',
            author=User.objects.get(username='SSS'),
        )
        response = self.authorized_client.get(reverse('follow_index'))
        post = response.context.get('page')[0].text
        response2 = self.authorized_client2.get(reverse('follow_index'))
        post2 = response2.context.get('page')
        self.assertEqual(post, 'Текст')
        self.assertFalse(post2)

    def test_create_comment(self):
        '''Авторизованный пользователь может оставить комментарий по валидной форме'''
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Коммент',
            'post': self.post
        }
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={'username': 'VVV', 'post_id': '1'}),
            data=form_data,
            follow=False
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, reverse(
            'post', kwargs={'username': comment.author,
                            'post_id': '1'}))

    def test_guest_not_have_rules_on_comments(self):
        '''Гость не может оставлять комментарии к постам'''
        form_data = {
            'text': 'Коммент',
            'post': self.post
        }
        self.authorized_client.post(
            reverse('add_comment', kwargs={'username': 'SSS', 'post_id': '1'}),
            data=form_data,
            follow=True
        )
        comments_count = Comment.objects.count()
        self.guest_client.post(
            reverse('add_comment', kwargs={'username': 'SSS', 'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
