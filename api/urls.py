from django.urls import path, include
from .views import (CropDataDetail,
                    CropDataDetailById,
                    ScenarioList,
                    ScenarioDetail, 
                    ScenarioCropsList,
                    CropDetailById,
                    CropList,
                    FarmCropDetailById,
                    )

v1_patterns = [
    path('crop/<int:pk>/', CropDetailById.as_view(),
         name='crop_id'),
    path('cropdata/name/<str:name>/', CropDataDetail.as_view(), 
         name='cropdata'),
    path('cropdata/pk/<int:pk>/', CropDataDetailById.as_view(),
         name='cropdata_id'),
    path('farmcrop/<int:pk>/', FarmCropDetailById.as_view(),
         name='farmcrop_id'),
    path('scenario/list/<int:fid>/', ScenarioList.as_view(),
         name='scenario_list'),
    path('scenario/<int:pk>/', ScenarioDetail.as_view(),
         name='scenario'),
    path('scenario/listcrops/<int:pk>/', ScenarioCropsList.as_view(),
         name='scenario_crops_list'),
    path('scenario/crops/<int:pk>/', CropList.as_view(),
         name='scenariocrops'),
]

urlpatterns = [
    path('v1/', include((v1_patterns, 'v1'), namespace='v1')),
]
