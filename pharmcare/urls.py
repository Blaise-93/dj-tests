from django.urls import path
from .views import (
    PatientDetailListView,
    PatientDetailCreateView,
    PatientDetailView,
    UpdatePatientDetailView,
    DeletePatientDetailView,

    MedicationHistoryListView,
    MedicationHistoryCreateView,
    MedicationHistoryDeleteView,
    MedicationHistoryUpdateView,
    MedicationHistoryDetailView,
    
    PatientListView,
    PatientCreateView,
    PatientsDetailView,
    PatientUpateView,
    PatientDeleteView,
    

)
app_name = 'pharmcare'

urlpatterns = [
    # Pharmcare URI
    path('', PatientDetailListView.as_view(), name='patient'),
    path('medication-history/', MedicationHistoryListView.as_view(),
         name='medication-history'),
    path('patient-list', PatientListView.as_view(), name='patients'),
      # pharmcare create views
    path('patient-create/', PatientDetailCreateView.as_view(), name='patient-create'),
    path('medication-history-create/', MedicationHistoryCreateView.as_view(),
         name='medication-history-create'),
    path('patients-create/', PatientCreateView.as_view(), name='patients-create'),
    
    
     path('<str:slug>/', PatientDetailView.as_view(), name='patient-detail'),
     path('<int:pk>/', MedicationHistoryDetailView.as_view(),
         name='medication-history-detail'), 
     path('<str:slug>/', PatientsDetailView.as_view(), name='patients-detail'),
    
     path('<str:slug>/patient-update/',
         UpdatePatientDetailView.as_view(), name='patient-update'),
     path('<int:pk>/medication-history-update/',
         MedicationHistoryUpdateView.as_view(), name='medication-history-update'),
     path('<str:slug>/patients-update/',
         PatientUpateView.as_view(), name='patients-update'),
    
    
   
    path('<str:slug>/patient-delete/',
         DeletePatientDetailView.as_view(), name='patient-delete'),

    path('<int:pk>/medication-history-delete/',
         MedicationHistoryDeleteView.as_view(), name='medication-history-delete'),
    
     path('<int:pk>/patients-delete/',
          PatientDeleteView.as_view(), name='patients-delete'),

    # Patients URI - Many to Many field
    
]
