from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from base.models import UserProfile, Follower, Post, Comment, Reply, Saved
import json


class TestViews(TestCase):
    # this method will be run before other tests
    def setUp(self):
        self.client = Client()

        # urls
        self.main_page_url = reverse('main_page')
        self.register_page_url = reverse('register_page')

        # creating models objects
        self.username = 'naruto'
        self.password = 'naruto123'
        self.email = 'naruto@gmail.com'
        self.image = 'media/images/test_image.png'

        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user_pforifle = UserProfile.objects.create(user=self.user, email=self.email)

        self.post = Post.objects.create(user=self.user, image=self.image)
        self.go_to_post_url = reverse('go_to_post', args=[self.post.id])

    # testing login
    def test_login(self):
        self.client.login(username=self.username, password=self.password) # login

        response = self.client.get(self.main_page_url)
        self.assertEqual(response.status_code, 200)

    # testing main_page url
    def test_main_page_GET(self):
        response = self.client.get(self.main_page_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/main_page.html')

    # testing register_page url
    def test_register_page_GET(self):
        response = self.client.get(self.register_page_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/main_page.html')

    # testing go_to_post page url
    def test_go_to_post_GET(self):
        # login (it must be logged in because of login_required decorator)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.go_to_post_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/go_to_post.html')
