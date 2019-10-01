from django.urls import path, include
from .views import (CropDataDetail,
                    CropDataDetailById,
                    ScenarioList,
                    ScenarioDetail, 
                    ScenarioCropsList,
                    CropTriangles,
                    CropList)

v1_patterns = [
    path('cropdata/<str:name>/', CropDataDetail.as_view(), name='cropdata'),
    path('cropdata/<int:id>/', CropDataDetailById.as_view(),
         name='cropdata_id'),
    path('scenario/list/<int:fid>/', ScenarioList.as_view(),
         name='scenario_list'),
    path('scenario/<int:pk>/', ScenarioDetail.as_view(),
         name='scenario'),
    path('scenario/listcrops/<int:pk>/', ScenarioCropsList.as_view(),
         name='scenario_crops_list'),
    path('crop/<int:pk>/', CropTriangles.as_view(),
         name='croptriangles'),
    path('scenario/crops/<int:pk>/', CropList.as_view(),
         name='scenariocrops'),
]

urlpatterns = [
    path('v1/', include((v1_patterns, 'v1'), namespace='v1')),
]
