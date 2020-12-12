from django.core.cache import cache
from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Group, Post, User
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='VVV',
            email='vv@mail.ru',
            password='123'
        )
        cls.other_user = User.objects.create(
            username='SSS',
            email='SS@mail.ru',
            password='123'
        )
        cls.group = Group.objects.create(
            title='cat',
            description='Test description',
            slug='cat'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=User.objects.get(username='VVV')
        )

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
        site = Site.objects.get(pk=1)
        self.flat_about.sites.add(site)
        self.flat_tech.sites.add(site)
        self.static_pages = ('/about-author/', '/about-spec/')
        self.guest_client = Client()
        self.user = User.objects.get(username='VVV')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_2 = Client()
        self.user_2.force_login(self.other_user)

    def test_static_pages_response(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')

    def test_quest_pages_response(self):
        '''Страница доступна любому пользователю'''
        self.urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': 'VVV'}),
            reverse('post', kwargs={'username': 'VVV', 'post_id': '1'}),
            reverse('group', kwargs={'slug': 'cat'}),
        ]
        for url in self.urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_authorized_pages_response(self):
        '''Страница доступна авторизованному пользователю'''
        self.urls = [
            reverse('new_post'),
        ]
        for url in self.urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        cache.clear()
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'cat'}),
            'new.html': reverse('new_post'),
            'new.html': reverse('post_edit', kwargs={'username': 'VVV', 'post_id': '1'}),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_user_post_edit(self):
        '''Страница /user/post_id/edit/ не доступна не авторизованному
        пользователю.'''
        response = self.guest_client.get(
            reverse('post_edit', kwargs={'username': 'VVV', 'post_id': '1'}), follow=True)
        self.assertRedirects(response, reverse('post', kwargs={'username':
                                                               'VVV',
                                                               'post_id':
                                                               '1'}))

    def test_post_edit_no_author(self):
        '''Страница /user/post_id/edit/ не доступна не автору поста.'''
        response = self.user_2.get(reverse('post_edit', kwargs={'username':
                                                                'VVV', 'post_id': '1'}), follow=True)
        self.assertRedirects(response, reverse('post', kwargs={'username':
                                                               'VVV',
                                                               'post_id':
                                                               '1'},)
                             )

    def test_post_edit_author(self):
        '''Страница /user/post_id/edit/ доступна автору поста.'''
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': 'VVV', 'post_id': '1'}))
        self.assertEqual(response.status_code, 200)

    def test_new_quest_redirect(self):
        '''Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина.
        '''
        response = self.guest_client.get(reverse('new_post'), follow=True)
        sum = reverse('login') + '?next=' + reverse('new_post')
        self.assertRedirects(response, sum)

    def test_404(self):
        '''Несуществующая страница выдаёт ошибку 404'''
        response = self.authorized_client.get('arbarbarb')
        self.assertEqual(response.status_code, 404)
