from django.urls import path
from .views import (
    PatientListView,
    PatientCreateView,
    PatientDetailView
)
app_name = 'pharmcare'

urlpatterns = [
     path('', PatientListView.as_view(), name='patient'),
     path('patient-create/', PatientCreateView.as_view(), name='patient-create'),
]
