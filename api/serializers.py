from rest_framework import serializers

from optimizer.models import CropData, Scenario, Crop, FarmCrop
import json


class CropDataSerializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField()
    yields = serializers.SerializerMethodField()
    gross  = serializers.SerializerMethodField()

    def get_prices(self, cropdata):
        return json.loads(cropdata.prices)
    def get_yields(self, cropdata):
        return json.loads(cropdata.yields)
    def get_gross(self, cropdata):
        return cropdata.gross()

    '''serializes CropData'''
    class Meta:
        model = CropData
        fields = ('name', 'unit', 'prices', 'yields', 'cost', 'gross', )


class FarmCropSerializer(serializers.ModelSerializer):
    name   = serializers.SerializerMethodField()
    unit   = serializers.SerializerMethodField()
    gross  = serializers.SerializerMethodField()
    cost   = serializers.SerializerMethodField()

    def get_name(self, farmcrop):
        return farmcrop.data.name
    def get_unit(self, farmcrop):
        return farmcrop.data.unit
    def get_gross(self, farmcrop):
        return farmcrop.gross()
    def get_cost(self, farmcrop):
        return farmcrop.cost()

    class Meta:
        model = FarmCrop
        fields = ('name', 'unit', 'gross', 'cost', )

class CropSerializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField()
    yields = serializers.SerializerMethodField()
    gross  = serializers.SerializerMethodField()
    name   = serializers.SerializerMethodField()
    unit   = serializers.SerializerMethodField()
    cost   = serializers.SerializerMethodField()

    def get_name(self, crop):
        return crop.data.name
    def get_unit(self, crop):
        return crop.data.unit
    def get_prices(self, crop):
        return json.loads(crop.prices())
    def get_yields(self, crop):
        return json.loads(crop.yields())
    def get_gross(self, crop):
        return crop.gross()
    def get_cost(self, crop):
        return crop.cost()

    class Meta:
        model = Crop
        fields = ('name', 'unit', 'prices', 'yields', 'gross', 'cost', )

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
