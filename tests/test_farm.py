from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth.models import User

from farm.models import Farm


class FarmTests(TestCase):
    def setUp(self):
        User.objects.create(username="foo", password="bar")
        User.objects.create(username="bar", password="foo")
        self.foo = Client()
        self.foo.login(username="foo", password="bar")
        self.bar = Client()
        self.bar.login(username="bar", password="foo")

        self.notloggedin = Client()

    def tearDown(self):
        pass

    def test_anonymous(self):
        url = reverse('home')

        res = self.notloggedin.get(url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
