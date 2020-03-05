from django.test import TestCase, Client
from .models import User, Post, Group, Comment, Follow
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core import mail
import time
# Create your tests here.


class ImageTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        user1 = {'name': 'sarah',
                 'surname': 'oconnor',
                 'username': 'sarah',
                 'email': 'ak47@yandex.fr',
                 'password1': 'zxnm11a!s',
                 'password2': 'zxnm11a!s'}
        self.client.post(reverse('signup'), user1, follow=True)
        self.client.login(username="sarah", password="zxnm11a!s")
        self.group = Group.objects.create(
            title='test123', slug='test', description='testing')
        self.text = 'cache text'
        with open('media/testimg.jpg', 'rb') as fp:
            self.client.post(reverse('new_post'), {
                             'text': 'fred', 'image': fp, 'group': 1}, follow=True)

    def test_post_image_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<img', response.content.decode())

    def test_post_image(self):
        response = self.client.get('/sarah/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<img', response.content.decode())

    def test_post_image_edit(self):
        response = self.client.get('/group/test/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<img', response.content.decode())

    def test_not_image(self):
        with open('media/test.txt', 'rb') as fp:
            response = self.client.post(reverse('new_post'),
                                        {'text': 'fred', 'image': fp, 'group': 1})
        self.assertFormError(response, 'form', 'image',
                             errors=('Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.'))

    def test_cache_with_creating_new_post(self):
        self.client.post(reverse('new_post'), {'text': self.text, 'group': 1})
        Post.objects.get(pk=2)
        response = self.client.get('/')
        self.assertNotContains(response, self.text, status_code=200, msg_prefix='', html=False)
        time.sleep(20)
        response = self.client.get('/')
        self.assertContains(response, self.text, status_code=200, msg_prefix='', html=False)

class FollowersTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        user1 = {'name': 'sarah',
                 'surname': 'oconnor',
                 'username': 'sarah',
                 'email': 'ak47@yandex.fr',
                 'password1': 'zxnm11a!s',
                 'password2': 'zxnm11a!s'}

        user2 = {'name': 'brian',
                 'surname': 'oconnor',
                 'username': 'brian',
                 'email': 'ak48@yandex.fr',
                 'password1': 'zxnm11a!s',
                 'password2': 'zxnm11a!s'}

        self.client.post(reverse('signup'), user1, follow=True)
        self.client.post(reverse('signup'), user2, follow=True)

        self.client.login(username="sarah", password="zxnm11a!s")
        self.group = Group.objects.create(
            title='test123', slug='test', description='testing')
        self.text = 'cache text'
        with open('media/testimg.jpg', 'rb') as fp:
            self.client.post(reverse('new_post'), {
                             'text': self.text, 'image': fp, 'group': 1}, follow=True)
        self.client.logout()
        self.client.login(username="brian", password="zxnm11a!s") 
        
        
#Только авторизированный пользователь может комментировать посты.
    def test_only_authorised_user_can_make_comments(self):
        test_comment = 'test_comment'
        response = self.client.post('/sarah/1/comment/', {'text': test_comment}, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/sarah/1/')
        self.assertContains(response, test_comment, status_code=200, msg_prefix='', html=False)   
        self.client.logout()
        response = self.client.post('/sarah/1/comment/', {'text': test_comment}, follow=True)
        self.assertRedirects(response,'/auth/login/?next=%2Fsarah%2F1%2Fcomment%2F', status_code=302, 
                        target_status_code=200, msg_prefix='', 
                        fetch_redirect_response=True)


#Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок.
    def test_user2_follows_to_user1(self):
        response = self.client.get('/sarah/follow')
        author1 = User.objects.get(username = 'brian')
        follower = Follow.objects.filter(user=author1).count()
        author2 = User.objects.get(username = 'sarah')
        following = Follow.objects.filter(author=author2).count()
        self.assertEqual(follower, following)
        self.assertEqual(follower, 1)
        response = self.client.get('/sarah/unfollow')
        follower = Follow.objects.filter(user=author1).count()
        following = Follow.objects.filter(author=author2).count()
        self.assertEqual(follower, following)
        self.assertEqual(follower, 0)
    
#Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех, кто не подписан на него.
    def test_new_post_is_shown_in_favourite_users(self):
        response = self.client.get('/sarah/follow') 
        response = self.client.get('/follow/')
        self.assertContains(response, self.text, status_code=200, msg_prefix='', html=False)
        response = self.client.get('/sarah/unfollow')
        response = self.client.get('/follow/')
        self.assertNotContains(response, self.text, status_code=200, msg_prefix='', html=False)
        Post.objects.create(author = User.objects.get(username='sarah'), text = 'favourite users')
        response = self.client.get('/follow/')
        self.assertNotContains(response, 'favourite users', status_code=200, msg_prefix='', html=False) 
        response = self.client.get('/sarah/follow') 
        response = self.client.get('/follow/')
        self.assertContains(response, self.text, status_code=200, msg_prefix='', html=False)



        





