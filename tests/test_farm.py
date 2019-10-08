from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth.models import User

from farm.models import Farm
from optimizer.models import CropData


class FarmTests(TestCase):
    fixtures = ['crop-data', ]

    def setUp(self):
        self.uFoo = User.objects.create_user(username="foo", password="bar")
        self.uBar = User.objects.create_user(username="bar", password="foo")
        self.foo = Client()
        self.foo.login(username="foo", password="bar")
        # this will create a farm for foo
        self.foo.get(reverse('home'), follow=True)

        self.bar = Client()
        self.bar.login(username="bar", password="foo")

        self.notloggedin = Client()

    def tearDown(self):
        pass

    # HOME page
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

    def test_farm(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm', args=(farm.id, ))

        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(farm, res.context['farm'}

    # ADD CROP TO FARM
    def test_addCrop_addone(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        incrops = [c.data.id for c in farm.crops.all()]
        outcrops = CropData.objects.exclude(id__in=incrops)
        outcrop = outcrops.first()
        crops = [outcrop.name, ]

        cnt = farm.crops.count()
        res = self.foo.post(url, dict(crops=crops))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(cnt + len(crops), farm.crops.count())

    def test_addCrop_addall(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        incrops = [c.data.id for c in farm.crops.all()]
        outcrops = CropData.objects.exclude(id__in=incrops)
        crops = [c.name for c in outcrops]

        cnt = farm.crops.count()
        res = self.foo.post(url, dict(crops=crops))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(cnt + len(crops), farm.crops.count())

    def test_addCrop_bad(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        crops = [farm.crops.first().data.name]

        cnt = farm.crops.count()
        res = self.foo.post(url, dict(crops=crops))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(cnt, farm.crops.count())

    def test_addCrop_bad2(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        crops = ['jellybeans', ]

        cnt = farm.crops.count()
        res = self.foo.post(url, dict(crops=crops))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(cnt, farm.crops.count())

    def test_addCrop_notloggedin(self):
        '''redirect to login page'''
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        cnt = farm.crops.count()
        res = self.notloggedin.post(url, dict(crops=['tobacco']), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
        self.assertEqual(cnt, farm.crops.count())

    def test_addCrop_wronguser(self):
        '''redirect to login page'''
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:add_crop', args=(farm.id, ))

        cnt = farm.crops.count()
        res = self.bar.post(url, dict(crops=['tobacco']))
        self.assertEqual(404, res.status_code)
        self.assertEqual(cnt, farm.crops.count())
