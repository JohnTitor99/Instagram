from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from base.views import mainPage, registerPage, logoutUser, goToPost
from base.models import Post


# urls with no arguments
class TestUrls(SimpleTestCase):
    def test_main_page_urls_resolves(self):
        url = reverse('main_page')
        self.assertEquals(resolve(url).func, mainPage)

    def test_register_page_url_resolves(self):
        url = reverse('register_page')
        self.assertEquals(resolve(url).func, registerPage)

    def test_logout_user_url_resolves(self):
        url = reverse('logout_user')
        self.assertEquals(resolve(url).func, logoutUser)


# urls with arguments
class TestUrlsArg(TestCase):
    def setUp(self):
        self.username = 'naruto'
        self.password = 'naruto123'
        self.image = 'media/images/test_image.png'

        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.post = Post.objects.create(user=self.user, image=self.image)

    def test_go_to_post_url_resolves(self):
        url = reverse('go_to_post', args=[self.post.id])
        self.assertEquals(resolve(url).func, goToPost)
