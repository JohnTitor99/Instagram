from django.test import SimpleTestCase
from base.forms import PostForm, RegistrationForm


class TestForms(SimpleTestCase):
    # POST FORM
    # testing insert data
    def test_post_form_valid_data(self):
        form = PostForm(data={
            'image_dimensions': '2'
        })
        self.assertTrue(form.is_valid())

    # testing empty data
    def test_post_form_no_data(self):
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
