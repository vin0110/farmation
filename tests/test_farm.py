from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth.models import User

from farm.models import Farm
from optimizer.models import CropData


class HomeTests(TestCase):
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

    # FARM page
    def test_farm(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:farm', args=(farm.id, ))

        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(farm, res.context['farm'])

    def test_farm_wrong(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:farm', args=(farm.id, ))

        res = self.bar.get(url)
        self.assertEqual(res.status_code, 404)

    def test_farm_notloggedin(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:farm', args=(farm.id, ))

        res = self.bar.get(url)
        self.assertEqual(res.status_code, 404)


class AddRmCropTests(TestCase):
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
        # this will create a farm for bar
        self.bar.get(reverse('home'), follow=True)

        self.notloggedin = Client()

    def tearDown(self):
        pass

    # REMOVE CROP FROM FARM
    def test_removeCrop(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:remove_crop', args=(crop.id, ))

        cnt = farm.crops.count()
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(cnt - 1, farm.crops.count())

    def test_removeCrop_wrong_crop(self):
        farm = Farm.objects.get(user=self.uFoo)
        barfarm = Farm.objects.get(user=self.uBar)

        url = reverse('farm:remove_crop', args=(barfarm.crops.first().id, ))

        cnt = farm.crops.count()
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(cnt, farm.crops.count())

    def test_removeCrop_wrong_user(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:remove_crop', args=(crop.id, ))

        cnt = farm.crops.count()
        res = self.bar.get(url)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(cnt, farm.crops.count())

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


class AcresTest(TestCase):
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

    # EDIT ACRES
    def test_editacres(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_acres', args=(crop.id, ))

        # clear limits
        L, H = 0, 0
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

        # change lo
        L = 100
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

        # change hi
        H = 500
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

        # change both
        L, H = 400, 800
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

    def test_editacres_bad(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_acres', args=(crop.id, ))

        # clear
        L, H = 0, 0
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

        # lo greater than hi
        res = self.foo.post(url, dict(lo_acres=800, hi_acres=400), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)
        self.assertContains(res, "not lower than")

    def test_editacres_bad1(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_acres', args=(crop.id, ))

        # clear
        L, H = 0, 0
        res = self.foo.post(url, dict(lo_acres=L, hi_acres=H), follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)

        # lo greater than hi
        res = self.foo.post(url, dict(lo_acres=-800, hi_acres=-400),
                            follow=True)
        self.assertEqual(res.status_code, 200)
        crop.refresh_from_db()
        lo, hi = crop.limits()
        self.assertEqual(L, lo)
        self.assertEqual(H, hi)
        # this string is in the field error
        self.assertContains(res, "greater")

    def test_editacres_wrong_user(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_acres', args=(crop.id, ))

        limits = crop.limits()
        res = self.bar.post(url, dict(lo_acres=100, hi_acres=400))
        self.assertEqual(404, res.status_code)

        crop.refresh_from_db()
        self.assertEqual(limits, crop.limits())

    def test_editacres_notloggedin(self):
        '''redirect to login page'''
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_acres', args=(crop.id, ))

        limits = crop.limits()
        res = self.notloggedin.post(url, dict(lo_acres=100, hi_acres=400),
                                    follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
        crop.refresh_from_db()
        self.assertEqual(limits, crop.limits())


class CostTest(TestCase):
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

    # EDIT ACRES
    def test_editCost(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_cost', args=(crop.id, ))

        for cost in [100.0, 100, -100.0, 1000000.888]:
            res = self.foo.post(url, dict(cost_override=cost))
            self.assertEqual(res.status_code, 302)
            crop.refresh_from_db()
            self.assertEqual(cost, crop.cost_override)

    def test_editCost_wrong_user(self):
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_cost', args=(crop.id, ))

        cost = crop.cost_override
        res = self.bar.post(url, dict(lo_acres=100, hi_acres=400))
        self.assertEqual(404, res.status_code)

        crop.refresh_from_db()
        self.assertEqual(cost, crop.cost_override)

    def test_editCost_notloggedin(self):
        '''redirect to login page'''
        farm = Farm.objects.get(user=self.uFoo)
        crop = farm.crops.first()
        url = reverse('farm:edit_cost', args=(crop.id, ))

        cost = crop.cost_override
        res = self.notloggedin.post(url, dict(lo_acres=100, hi_acres=400),
                                    follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
        crop.refresh_from_db()
        self.assertEqual(cost, crop.cost_override)


class ExpenseTest(TestCase):
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

    # EDIT ACRES
    def test_editExpense(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:edit_expense', args=(farm.id, ))

        for expense in [100000.0, 100.0, 9876543.21]:
            res = self.foo.post(url, dict(max_expense=expense))
            self.assertEqual(res.status_code, 302)
            farm.refresh_from_db()
            self.assertEqual(expense, farm.max_expense)

    def test_editExpense_wrong_user(self):
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:edit_expense', args=(farm.id, ))

        expense = farm.max_expense
        res = self.bar.post(url, dict(max_expense=expense))
        self.assertEqual(404, res.status_code)

        farm.refresh_from_db()
        self.assertEqual(expense, farm.max_expense)

    def test_editExpense_notloggedin(self):
        '''redirect to login page'''
        farm = Farm.objects.get(user=self.uFoo)
        url = reverse('farm:edit_expense', args=(farm.id, ))

        expense = farm.max_expense
        res = self.notloggedin.post(url, dict(max_expense=expense),
                                    follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
        farm.refresh_from_db()
        self.assertEqual(expense, farm.max_expense)
