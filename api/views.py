from rest_framework import generics

from django.http import JsonResponse
from optimizer.models import (CropData,
                              Scenario, 
                              Crop,
                              FarmCrop, )

from .serializers import (CropDataSerializer,
                          ScenarioListSerializer,
                          ScenarioDetailSerializer, 
                          CropSerializer,
                          FarmCropSerializer,
                          )


class CropDetailById(generics.RetrieveAPIView):
    '''Return Crop by pk'''
    serializer_class = CropSerializer
    queryset = Crop.objects.all()


class CropDataDetail(generics.RetrieveAPIView):
    '''Return Cropdata by name'''
    serializer_class = CropDataSerializer
    queryset = CropData.objects.all()
    lookup_field = 'name'


class CropDataDetailById(generics.RetrieveAPIView):
    '''Return CropData by pk'''
    serializer_class = CropDataSerializer
    queryset = CropData.objects.all()


class FarmCropDetailById(generics.RetrieveAPIView):
    '''Return FarmCrop by pk'''
    serializer_class = FarmCropSerializer
    queryset = FarmCrop.objects.all()


class ScenarioDetail(generics.RetrieveAPIView):
    '''Return scenario by id'''
    serializer_class = ScenarioDetailSerializer

    def get_queryset(self):
        scenario = Scenario.objects.filter(pk=self.kwargs['pk'])
        scenario.first().analyzeScenario() 
        return scenario


class ScenarioList(generics.ListAPIView):
    '''list scenarios by farm'''
    serializer_class = ScenarioListSerializer

    def get_queryset(self):
        return Scenario.objects.filter(farm__id=self.kwargs['fid'])


class ScenarioCropsList(generics.GenericAPIView):
    '''Returns list of crop names in scenario'''

    def get(self, request, pk):
        scenario = Scenario.objects.get(pk=pk)
        scenario_crops = scenario.crops.all()
        data = { 'cropnames': [ c.data.name for c in scenario_crops ] }
        return JsonResponse(data)


class CropList(generics.ListAPIView):
    '''list scenarios by farm'''
    serializer_class = CropSerializer

    def get_queryset(self):
        return Crop.objects.filter(scenario_id=self.kwargs['pk'])
