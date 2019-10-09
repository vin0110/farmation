from rest_framework import serializers

from optimizer.models import CropData, Scenario, Crop
import json


class CropDataSerializer(serializers.ModelSerializer):
    '''serializes CropData'''
    class Meta:
        model = CropData
        fields = ('name', 'unit', 'prices', 'yields', )

class CropSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    price_triangle = serializers.SerializerMethodField()
    yield_triangle = serializers.SerializerMethodField()

    def get_yield_triangle(self, crop):
        return json.loads(crop.data.yields)
    def get_price_triangle(self, crop):
        return json.loads(crop.data.prices)
    def get_name(self, crop):
        return crop.data.name
    def get_unit(self, crop):
        return crop.data.unit
    def get_cost(self, crop):
        return crop.data.cost

    class Meta:
        model = Crop
        fields = ('name', 'unit', 'price_triangle', 'yield_triangle', 'cost')

class ScenarioListSerializer(serializers.ModelSerializer):
    '''serializes scenarios for a farm'''
    farm_name = serializers.SerializerMethodField()

    def get_farm_name(self, scenario):
        return scenario.farm.name

    class Meta:
        model = Scenario
        fields = ('id', 'name', 'farm_name', 'state',
                  'mean', 'mean_partition',
                  'q1', 'q1_partition',
                  'q3', 'q3_partition', )

class ScenarioDetailSerializer(serializers.ModelSerializer):
    '''serializes scenario'''
    class Meta:
        model = Scenario
        exclude = []
