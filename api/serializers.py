from rest_framework import serializers

from optimizer.models import CropData, Scenario


class CropDataSerializer(serializers.ModelSerializer):
    '''serializes CropData'''
    class Meta:
        model = CropData
        fields = ('name', 'unit', 'price_histo')


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
