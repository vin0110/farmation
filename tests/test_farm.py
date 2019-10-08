from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth.models import User

from farm.models import Farm


class FarmTests(TestCase):
    fixtures = ['crop-data', ]

    def setUp(self):
        User.objects.create_user(username="foo", password="bar")
        User.objects.create_user(username="bar", password="foo")
        self.foo = Client()
        rc = self.foo.login(username="foo", password="bar")
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

    def test_home(self):
        url = reverse('home')

        res = self.foo.get(url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, len(res.context['farms']))

    def test_different_users(self):
        url = reverse('home')

        res = self.foo.get(url, follow=True)
        self.assertEqual(res.status_code, 200)
        fooFarm = res.context['farms'][0]

        res = self.bar.get(url, follow=True)
        self.assertEqual(res.status_code, 200)
        barFarm = res.context['farms'][0]

        self.assertNotEqual(fooFarm.id, barFarm.id)
