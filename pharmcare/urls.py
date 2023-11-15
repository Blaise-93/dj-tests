from django.urls import path
from .views import (
    PatientListView,
    PatientCreateView,
    PatientDetailView,
    UpdatePatientDetailView,
    DeletePatientView
)
app_name = 'pharmcare'

urlpatterns = [
     path('', PatientListView.as_view(), name='patient'), 
     path('patient-create/', PatientCreateView.as_view(), name='patient-create'),
     path('<str:slug>/', PatientDetailView.as_view(), name='patient-detail'),
     path('<str:slug>/patient-update/', UpdatePatientDetailView.as_view(), name='patient-update'),
     path('<str:slug>/patient-delete/', DeletePatientView.as_view(), name='patient-delete'),
]
