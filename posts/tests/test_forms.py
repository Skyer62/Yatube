from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Post, Group, User
from django.test import Client, TestCase


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='VVV',
            email='vv@mail.ru',
            password='123'
        )
        cls.user2 = User.objects.create(
            username='SSS',
            email='ss@mail.ru',
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
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        text_file = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.image = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        self.txt = SimpleUploadedFile(
            name='text.txt',
            content=text_file,
            content_type='text/txt'
        )

    # Тест картинки
    def test_create_post(self):
        '''Валидная форма создает post. Пост появляется в бд. Картинка появляется в посте'''
        image = self.image
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': image,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=False
        )
        response2 = self.authorized_client.get(reverse('index'))
        post = response2.context['page'][0]
        self.assertEqual(post.image.size, image.size)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        '''При редактировании поста он изменяеся в бд'''
        form_data = {
            'group': Group.objects.get().id,
            'text': 'asd',
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                    'username': self.user, 'post_id': Post.objects.first().id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(post.text, 'asd')

    # Вроде этот тест убрали(почитал в slack)
    def test_no_image_file_upload(self):
        '''Нельзя загрузить txt файл вместо картинки'''
        text = self.txt
        form = {
            'text': 'Текст',
            'image': text,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form,
            follow=False
        )
        self.assertFormError(response, 'form', 'image', "Формат файлов 'txt' не поддерживается. Поддерживаемые форматы файлов: 'bmp, dib, gif, tif, tiff, jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, blp, bufr, cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, iim, mpg, mpeg, mpo, msp, palm, pcd, pdf, pxr, psd, bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, wmf, emf, xbm, xpm'.")
