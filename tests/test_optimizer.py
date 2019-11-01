from django.test import TestCase
from django.test import Client
from django.test import tag

from django.urls import reverse
from django.contrib.auth.models import User

from farm.models import Farm
from optimizer.models import CropData
from optimizer.models import Crop
from optimizer.models import Scenario

from optimizer.forms import EditTriangleForm

import json

class ScenarioTests(TestCase):
    fixtures = ['crop-data', ]

    @tag('slow')
    def setUp(self):
        # Creating user and logging in.
        self.uFoo = User.objects.create_user(username="foo", password="bar")
        self.foo = Client()
        self.foo.login(username="foo", password="bar")

        # 
        self.uBar = User.objects.create_user(username="bar", password="foo")
        self.bar = Client()
        self.bar.login(username="bar", password="foo")

        # Creating user who doesn't login.
        self.notloggedin = Client()

        # Entering site and getting user's farm.
        self.foo.get(reverse('home'), follow=True)
        self.farm = Farm.objects.get(user=self.uFoo)

        # Adding two scenarios. Should be called "one" and "two".
        self.foo.get(reverse('optimizer:scenario_add', args=(self.farm.pk,)),
            follow=True)
        self.foo.get(reverse('optimizer:scenario_add', args=(self.farm.pk,)),
            follow=True)
        self.scenarios = self.farm.scenarios.all()
        self.scen_one = self.scenarios[0]

    @tag('slow')
    def tearDown(self):
        pass

    @tag('slow')
    def test_scenarioList(self):
        url = reverse('optimizer:list', args=(self.scenarios[0].pk,))
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEquals(res.context['farm'], self.farm)
        self.assertTemplateUsed(res, "optimizer/list.html")

    @tag('slow')
    def test_scenarioList_invalidpk(self):
        url = reverse('optimizer:list', args=(1928173,))
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 404)

    @tag('slow')
    def test_scenarioAdd(self):
        orig_count = len( self.scenarios )
        self.foo.get(reverse('optimizer:scenario_add', args=(self.farm.pk,)),
            follow=True)
        new_count = len(self.farm.scenarios.all())
        self.assertEqual( new_count, orig_count + 1)

    @tag('slow')
    def test_scenarioAdd_invalidfarmpk(self):
        res = self.foo.get(reverse('optimizer:scenario_add', args=(9999,)), follow=True)
        self.assertEqual(res.status_code, 404)

    @tag('slow')
    def test_scenarioAdd_usernotloggedin(self):
        res = self.notloggedin.get(reverse('optimizer:scenario_add',
            args=(self.farm.pk,)), follow=True)
        # Shouldn't this be a 404 error?.
        #self.assertEqual(res.status_code, 404)
        self.assertEqual(res.status_code, 200)

    @tag('slow')
    def test_scenarioDelete(self):
        self.assertEqual(len( self.farm.scenarios.all() ), 2)
        self.assertEqual(self.farm.scenarios.all()[1].name, 'two')

        res = self.foo.get(reverse('optimizer:scenario_delete',
            args=(self.scenarios[1].pk,)), follow=True)

        self.assertEqual(len( self.farm.scenarios.all() ), 1)
        self.assertEqual(self.farm.scenarios.all()[0].name, 'one')

    @tag('slow')
    def test_scenarioDelete_invalidscenariopk(self):
        numScens = len(self.farm.scenarios.all())
        res = self.foo.get(reverse('optimizer:scenario_delete',
            args=(9999,)), follow=True)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(numScens, len(self.farm.scenarios.all()))

    @tag('slow')
    def test_scenarioDetails(self):
        res = self.foo.get(reverse('optimizer:scenario_details', 
            args=(self.scen_one.pk,)), follow=True)
        self.assertEqual(res.status_code, 200)

    @tag('slow')
    def test_scenarioDetails_nofarmcrops(self):
        res = self.foo.get(reverse('optimizer:scenario_details', 
            args=(self.scen_one.pk,)), follow=True)
        self.assertNotContains(res, 'No crops')

        # Deleting crops.
        self.assertNotEqual( 0, len( self.farm.crops.all()))
        self.farm.crops.all().delete()
        self.assertEqual( 0, len( self.farm.crops.all()))

        res = self.foo.get(reverse('optimizer:scenario_details', 
            args=(self.scen_one.pk,)), follow=True)
        self.assertContains( res, 'No crops', 1)

    @tag('slow')
    def test_scenarioDetails_namechange(self):
        self.assertEqual('one', self.scen_one.name)

        # Sets new name via POST request.
        res = self.foo.post(reverse('optimizer:scenario_details', 
            args=(self.scen_one.pk,)), dict(name='newScenarioName'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.farm.scenarios.all()[0].name, 'newScenarioName')

    @tag('slow')
    def test_addCropToScenario(self):
        # Deletes any crops added to scenario "one".
        self.farm.scenarios.all()[0].crops.all().delete()

        # List of FarmCrops that can be added.
        availCrops = self.farm.crops.all()
        
        # Number of crops in scenario. Should be 0
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(0, numCrops)

        # Adding first crop to scenario "one".
        res = self.foo.post(reverse('optimizer:addCropScenario', 
            args=(self.scen_one.pk,)), 
            dict(crops=availCrops.first().data.name))

        numCrops = len(self.farm.scenarios.all()[0].crops.all())

        # Adding second crop to scenario "one".
        res = self.foo.post(reverse('optimizer:addCropScenario', 
            args=(self.scen_one.pk,)), 
            dict(crops=availCrops.last().data.name))
        self.assertEqual( numCrops + 1, len(self.farm.scenarios.all()[0].crops.all()))

    @tag('slow')
    def test_addCropToScenario_unavailablecrop(self):
        # Removes some FarmCrop.
        numFarmCrops = len(self.farm.crops.all())
        aFarmCrop = self.farm.crops.all().first()
        aFarmCrop.delete()
        self.assertEqual(numFarmCrops - 1, len(self.farm.crops.all()))

        # Deleting any crops added to scenario "one".
        self.farm.scenarios.all()[0].crops.all().delete()
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(0, numCrops)

        # Attempting to add the removed FarmCrop to a Scenario.
        res = self.foo.post(reverse('optimizer:addCropScenario', 
            args=(self.scen_one.pk,)), 
            dict(crops=aFarmCrop.data.name))

        # Asserting that the crop wasn't added to the Scenario.
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(0, numCrops)
        self.assertEqual(res.status_code, 200)

    @tag('slow')
    def test_addCropToScenario_wronguser(self):
        # Deleting any crops added to scenario "one".
        self.farm.scenarios.all()[0].crops.all().delete()
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(0, numCrops)

        # List of FarmCrops that can be added.
        availCrops = self.farm.crops.all()
        
        # Adding first available crop to scenario "one".
        res = self.bar.post(reverse('optimizer:addCropScenario', 
            args=(self.scen_one.pk,)), 
            dict(crops=availCrops.first().data.name))
        self.assertEqual(res.status_code, 404)

        # Asserting that the crop wasn't added to the Scenario.
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(0, numCrops)

    @tag('slow')
    def test_scenarioDetails_addallfarmcrops(self):
        # Adding all available FarmCrops to Scenario.
        for farmCrop in self.farm.crops.all():
            self.foo.post(reverse('optimizer:addCropScenario', 
                args=(self.scen_one.pk,)), 
                dict(crops=farmCrop.data.name))

        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        numFarmCrops = len(self.farm.crops.all())
        self.assertEqual(numCrops, numFarmCrops)

        # Getting any crops not added to Farm.
        incrops = [c.data.id for c in self.farm.crops.all()]
        unavailCrops = CropData.objects.exclude(id__in=incrops)

        # Attempting to add a FarmCrop that hasn't been added to the Scenario.
        someFarmCrop = unavailCrops.first()
        numCrops = len(self.farm.scenarios.all()[0].crops.all())
        
        # Navigating to Scenario Details page, then clicking 'Add Crops'.
        self.foo.get(reverse('optimizer:scenario_details', args=(self.scen_one.pk,)), follow=True)
        res = self.foo.get(reverse('optimizer:addCropScenario', args=(self.scen_one.pk,)), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains( res, 'All crops allowed in this farm have been added. Must reconfigure farm to add more crops.', 1 )

    @tag('slow')
    def test_scenarioDetails_addallcrops(self):
        # Getting all FarmCrops not added to Scenario.
        incrops = [c.data.id for c in self.farm.crops.all()]
        remainingCrops = CropData.objects.exclude(id__in=incrops)
        crops = [c.name for c in remainingCrops]

        # Adding all crops in system to the farm.
        url = reverse('farm:add_crop', args=(self.farm.id, ))
        res = self.foo.post(url, dict(crops=crops))
        numFarmCrops = len(self.farm.crops.all())
        numCropsInSystem  = len(CropData.objects.all())
        self.assertEqual(numCropsInSystem, numFarmCrops)

        # Adding all available FarmCrops to Scenario.
        for farmCrop in self.farm.crops.all():
            self.foo.post(reverse('optimizer:addCropScenario', 
                args=(self.scen_one.pk,)), 
                dict(crops=farmCrop.data.name))

        numCropsInScenario = len(self.farm.scenarios.all()[0].crops.all())
        self.assertEqual(numCropsInSystem, numCropsInScenario)

        # Attempting to add another crop to Scenario (non should be available on Farm or in System)
        self.foo.get(reverse('optimizer:scenario_details', args=(self.scen_one.pk,)), follow=True)
        res = self.foo.get(reverse('optimizer:addCropScenario', args=(self.scen_one.pk,)), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains( res, 'All crops have been added to this scenario.', 1)

    @tag('slow')
    def test_editcost(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_cost', args=(crop.id, ))

        for cost in [100.0, 100, -100.0, 1000000.888]:
            res = self.foo.post(url, dict(cost_override=cost), follow=True)
            self.assertEqual(res.status_code, 200)
            crop.refresh_from_db()
            self.assertEqual(cost, crop.cost_override)
   
    @tag('slow')
    def test_editCost_wronguser(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_cost', args=(crop.pk, ))

        cost = crop.cost_override
        res = self.bar.post(url, dict(cost_override=cost), follow=True)
        self.assertEqual(404, res.status_code)

        crop.refresh_from_db()
        self.assertEqual(cost, crop.cost_override)
        
    @tag('slow')
    def test_editCost_notloggedIn(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_cost', args=(crop.id, ))

        cost = crop.cost_override
        res = self.notloggedin.post(url, dict(cost_override=cost), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual('registration/login.html', res.template_name[0])
        self.assertTemplateUsed(res, 'registration/login.html')
        crop.refresh_from_db()
        self.assertEqual(cost, crop.cost_override)

    @tag('slow')
    def test_editCost_getrequest(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_cost', args=(crop.id, ))

        # Checking that form's initial value is correct.
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'optimizer/edit_cost.html')
        self.assertEqual(crop.cost_override, res.context['form'].initial['cost_override'])
        self.assertEqual(0.0, res.context['form'].initial['cost_override'])

        # Checking that the form displays a cost override if one exists.
        NEW_COST = 100.0
        crop.cost_override = NEW_COST
        crop.save()
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(NEW_COST, res.context['form'].initial['cost_override'])

    @tag('slow')
    def test_editTriangle_getrequest(self):
        crop = self.scen_one.crops.first()

        price_url = reverse('optimizer:edit_crop_price', args=(crop.id, ))
        yield_url = reverse('optimizer:edit_crop_yield', args=(crop.id, ))

        ## Testing without price and yield overrides.
        price_res = self.foo.get(price_url)
        yield_res = self.foo.get(yield_url)

        # Getting expected price and yield triangles.
        low_price, peak_price, high_price = json.loads(crop.prices())
        low_yield, peak_yield, high_yield = json.loads(crop.yields())

        # Checking that initial form values are correct.
        self.assertEqual(price_res.context['form'].initial['low'], low_price)
        self.assertEqual(price_res.context['form'].initial['peak'], peak_price)
        self.assertEqual(price_res.context['form'].initial['high'], high_price)

        self.assertEqual(yield_res.context['form'].initial['low'], low_yield)
        self.assertEqual(yield_res.context['form'].initial['peak'], peak_yield)
        self.assertEqual(yield_res.context['form'].initial['high'], high_yield)

        ## Testing with overrides.
        price_override = [1, 2, 3]
        yield_override = [11, 22, 33]

        # Overriding price and yield.
        crop.price_override = json.dumps(price_override)
        crop.yield_override = json.dumps(yield_override)
        crop.save()

        low_price, peak_price, high_price = json.loads(crop.prices())
        low_yield, peak_yield, high_yield = json.loads(crop.yields())

        price_res = self.foo.get(price_url)
        yield_res = self.foo.get(yield_url)

        # Checking that initial form values are correct.
        self.assertEqual(price_res.context['form'].initial['low'], low_price)
        self.assertEqual(price_res.context['form'].initial['peak'], peak_price)
        self.assertEqual(price_res.context['form'].initial['high'], high_price)

        self.assertEqual(yield_res.context['form'].initial['low'], low_yield)
        self.assertEqual(yield_res.context['form'].initial['peak'], peak_yield)
        self.assertEqual(yield_res.context['form'].initial['high'], high_yield)

    @tag('slow')
    def test_editTriangle_price(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_price', args=(crop.id, ))

        prices = [
            {'low':100.0, 'peak':150.0, 'high':200.0}, 
            {'low':1, 'peak':2, 'high':3},
            {'low':0, 'peak':1, 'high':2},
        ]

        for price in prices:
            res = self.foo.post(url, dict(low=price['low'],peak=price['peak'],
                high=price['high']), follow=True)
            self.assertEqual(res.status_code, 200)

            crop.refresh_from_db()
            price_triangle = json.loads(crop.prices())
            self.assertEqual(price_triangle[0], price['low'])
            self.assertEqual(price_triangle[1], price['peak'])
            self.assertEqual(price_triangle[2], price['high'])
   
    @tag('slow')
    def test_editTriangle_price_wronguser(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_price', args=(crop.id, ))

        self.assertFalse(crop.isPriceOverride())
        init_prices = json.loads(crop.prices())

        # Attempts to override this crop's prices.
        new_price = [100.0, 150.0, 200.0]
        res = self.bar.post(url, dict(low=new_price[0], peak=new_price[1],
            high=new_price[2]), follow=True)

        self.assertEqual(404, res.status_code)

        crop.refresh_from_db()
        curr_prices = json.loads(crop.prices())
        self.assertFalse(crop.isPriceOverride())
        self.assertEqual(curr_prices, init_prices)
        
    @tag('slow')
    def test_editTriangle_price_notloggedin(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_price', args=(crop.id, ))

        self.assertFalse(crop.isPriceOverride())
        init_prices = json.loads(crop.prices())

        # Attempts to override this crop's prices.
        new_price = [100.0, 150.0, 200.0]
        res = self.notloggedin.post(url, dict(low=new_price[0], peak=new_price[1],
            high=new_price[2]), follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'registration/login.html')

        crop.refresh_from_db()
        curr_prices = json.loads(crop.prices())
        self.assertFalse(crop.isPriceOverride())
        self.assertEqual(curr_prices, init_prices)
    
    @tag('slow')
    def test_editTriangle_price_reset(self):
        crop = self.scen_one.crops.first()

        self.assertFalse(crop.isPriceOverride())

        # Overriding the crop's prices.
        new_prices = json.dumps([123.0, 234.0, 345.0])
        crop.price_override = new_prices
        crop.save()

        self.assertEquals(crop.prices(), new_prices)
        self.assertTrue(crop.isPriceOverride())

        # Resetting the crop's prices.
        url = reverse('optimizer:reset_crop_price', args=(crop.id, ))
        res = self.foo.get(url, follow=True)
        self.assertEqual(res.status_code, 200)

        crop.refresh_from_db()
        self.assertFalse(crop.isPriceOverride())
        self.assertNotEquals(crop.prices(), new_prices)

    @tag('slow')
    def test_editTriangle_yield(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_yield', args=(crop.id, ))

        yields = [
            {'low':100.0, 'peak':150.0, 'high':200.0}, 
            {'low':1, 'peak':2, 'high':3},
            {'low':0, 'peak':1, 'high':2},
        ]

        for this_yield in yields:
            res = self.foo.post(url, dict(low=this_yield['low'],peak=this_yield['peak'],
                high=this_yield['high']), follow=True)
            self.assertEqual(res.status_code, 200)

            crop.refresh_from_db()
            yield_triangle = json.loads(crop.yields())
            self.assertEqual(yield_triangle[0], this_yield['low'])
            self.assertEqual(yield_triangle[1], this_yield['peak'])
            self.assertEqual(yield_triangle[2], this_yield['high'])

    @tag('slow')
    def test_editTriangle_yield_wronguser(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_yield', args=(crop.id, ))

        self.assertFalse(crop.isYieldOverride())
        init_yields = json.loads(crop.yields())

        # Attempts to override this crop's yields.
        new_yield = [100.0, 150.0, 200.0]
        res = self.bar.post(url, dict(low=new_yield[0], peak=new_yield[1],
            high=new_yield[2]), follow=True)

        self.assertEqual(404, res.status_code)

        crop.refresh_from_db()
        curr_yields = json.loads(crop.yields())
        self.assertFalse(crop.isYieldOverride())
        self.assertEqual(curr_yields, init_yields)

    @tag('slow')
    def test_editTriangle_yield_notloggedin(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_yield', args=(crop.id, ))

        self.assertFalse(crop.isYieldOverride())
        init_yields = json.loads(crop.yields())

        # Attempts to override this crop's yields.
        new_yield = [100.0, 150.0, 200.0]
        res = self.notloggedin.post(url, dict(low=new_yield[0], peak=new_yield[1],
            high=new_yield[2]), follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'registration/login.html')

        crop.refresh_from_db()
        curr_yields = json.loads(crop.yields())
        self.assertFalse(crop.isYieldOverride())
        self.assertEqual(curr_yields, init_yields)
 
    @tag('slow')
    def test_editTriangle_yield_reset(self):
        crop = self.scen_one.crops.first()

        self.assertFalse(crop.isYieldOverride())

        # Overriding the crop's yields.
        new_yields = json.dumps([123.0, 234.0, 345.0])
        crop.yield_override = new_yields
        crop.save()

        self.assertEquals(crop.yields(), new_yields)
        self.assertTrue(crop.isYieldOverride())

        # Resetting the crop's yields.
        url = reverse('optimizer:reset_crop_yield', args=(crop.id, ))
        res = self.foo.get(url, follow=True)
        self.assertEqual(res.status_code, 200)

        crop.refresh_from_db()
        self.assertFalse(crop.isYieldOverride())
        self.assertNotEquals(crop.yields(), new_yields)

    @tag('slow')
    def test_editTriangle_invalidvalues(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_crop_price', args=(crop.id, ))

        invalid_prices = [
            {'low':2, 'peak':1, 'high':3}, 
            {'low':2, 'peak':3, 'high':1}, 
            {'low':3, 'peak':2, 'high':1},
            {'low':3, 'peak':1, 'high':2},
            {'low':1, 'peak':3, 'high':2},
            {'low':1, 'peak':1, 'high':2},
            {'low':2, 'peak':2, 'high':3},
            {'low':2, 'peak':3, 'high':3},
        ]

        for price in invalid_prices:
            res = self.foo.post(url, dict(low=price['low'],peak=price['peak'],
                high=price['high']))
            self.assertEqual(res.status_code, 200)
            self.assertFormError(res, 'form', None, 
                'failed assertation: low < peak < high')

            crop.refresh_from_db()
            price_triangle = json.loads(crop.prices())
            self.assertNotEqual(price_triangle[0], price['low'])
            self.assertNotEqual(price_triangle[1], price['peak'])
            self.assertNotEqual(price_triangle[2], price['high'])
        
    @tag('slow')
    def test_editAcres(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_acres', args=(crop.id, ))

        self.assertEqual(crop.lo_acres, 0)
        self.assertEqual(crop.hi_acres, 0)

        valid_limits = [
            {'lo': 0, 'hi': 0},
            {'lo': 0, 'hi': 100},
            {'lo': 50, 'hi': 150},
            {'lo': 100, 'hi': 100},
            {'lo': 100, 'hi': 0}
        ]

        for limits in valid_limits:
            res = self.foo.post(url, dict(lo_acres=limits['lo'], hi_acres=limits['hi']), follow=True)
            self.assertEqual(res.status_code, 200)
            self.assertTemplateUsed(res, "optimizer/scenario_details.html")

            crop.refresh_from_db()
            lo, hi = crop.limits()
            self.assertEqual(limits['lo'], lo)
            self.assertEqual(limits['hi'], hi)

    @tag('slow')
    def test_editAcres_invalidlimits(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_acres', args=(crop.id, ))

        self.assertEqual(crop.lo_acres, 0)
        self.assertEqual(crop.hi_acres, 0)

        init_lo, init_hi = crop.limits()

        invalid_limits = [
            {'lo': 400, 'hi': 100},
        ]

        for limits in invalid_limits:
            res = self.foo.post(url, dict(lo_acres=limits['lo'], hi_acres=limits['hi']))
            self.assertEqual(res.status_code, 200)
            self.assertTemplateUsed(res, "optimizer/edit_acres.html")
            self.assertFormError(res, 'form', None, 
                'low is not lower than high')

            crop.refresh_from_db()
            lo, hi = crop.limits()
            self.assertEqual(init_lo, lo)
            self.assertEqual(init_hi, hi)

    @tag('slow')
    def test_editAcres_getrequest(self):
        crop = self.scen_one.crops.first()
        url = reverse('optimizer:edit_acres', args=(crop.id, ))

        self.assertEqual(crop.lo_acres, 0)
        self.assertEqual(crop.hi_acres, 0)

        # Checking that the form's inital values are correct.
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'optimizer/edit_acres.html')
        self.assertEqual(res.context['form'].initial['lo_acres'], crop.lo_acres)
        self.assertEqual(res.context['form'].initial['hi_acres'], crop.hi_acres)

        # Checking that the form's initial values update when acreage limits are changed.
        NEW_LO = 500
        NEW_HI = 1000
        crop.lo_acres = NEW_LO
        crop.hi_acres = NEW_HI
        crop.save()
        res = self.foo.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['form'].initial['lo_acres'], NEW_LO)
        self.assertEqual(res.context['form'].initial['hi_acres'], NEW_HI)
