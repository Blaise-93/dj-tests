from django.urls import path
from .views import (
    PatientListView,
    PatientCreateView,
    PatientDetailView,
    UpdatePatientDetailView,
    DeletePatientView,

    MedicationHistoryListView,
    MedicationHistoryCreateView,
    MedicationHistoryDeleteView,
    MedicationHistoryUpdateView,
    MedicationHistoryDetailView

)
app_name = 'pharmcare'

urlpatterns = [
    # PatientDetail URI
    
    path('', PatientListView.as_view(), name='patient'),
    path('medication-history/', MedicationHistoryListView.as_view(),
         name='medication-history'),
    
      # pharmcare create views
    path('patient-create/', PatientCreateView.as_view(), name='patient-create'),
    path('medication-history-create/', MedicationHistoryCreateView.as_view(),
         name='medication-history-create'),
    
     path('<int:pk>/', MedicationHistoryDetailView.as_view(),
         name='medication-history-detail'), 
     
      
     path('<str:slug>/', PatientDetailView.as_view(), name='patient-detail'),
    
     path('<int:pk>/medication-history-update/',
         MedicationHistoryUpdateView.as_view(), name='medication-history-update'),

   
    path('<str:slug>/patient-update/',
         UpdatePatientDetailView.as_view(), name='patient-update'),
    
    
   
    path('<str:slug>/patient-delete/',
         DeletePatientView.as_view(), name='patient-delete'),

    # Medication History URI

    path('<int:pk>/medication-history-delete/',
         MedicationHistoryDeleteView.as_view(), name='medication-history-delete'),

    # Patients URI - Many to Many field
    
]
