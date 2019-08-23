from rest_framework import generics

from django.http import JsonResponse
from optimizer.models import (CropData,
                              Scenario, 
                              Crop, )

from .serializers import (CropDataSerializer,
                          ScenarioListSerializer,
                          ScenarioDetailSerializer, 
                          )


class CropDataDetail(generics.RetrieveAPIView):
    '''Return cropdata by name'''
    serializer_class = CropDataSerializer
    queryset = CropData.objects.all()
    lookup_field = 'name'


class CropDataDetailById(generics.RetrieveAPIView):
    '''Return cropdata by id'''
    serializer_class = CropDataSerializer
    queryset = CropData.objects.all()


class ScenarioDetail(generics.RetrieveAPIView):
    '''Return scenario by id'''
    serializer_class = ScenarioDetailSerializer
    queryset = Scenario.objects.all()


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
