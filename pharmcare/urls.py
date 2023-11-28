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
    
    MedicationChangesListView,
    MedicationChangesCreateView,
    MedicationChangesDetailView,
    MedicationChangesUpdateView,
    MedicationChangesDeleteView,
    
    
    AnalysisOfClinicalProblemListView,
    AnalysisOfClinicalProblemCreateView,
    AnalysisOfClinicalProblemDetailView,
    AnalysisOfClinicalProblemUpdateView,
    AnalysisOfClinicalProblemDeleteView,
    

)
app_name = 'pharmcare'

urlpatterns = [
    # Pharmcare URI
    
        # pharmcare list URIs
    path('', PatientDetailListView.as_view(), name='patient'),
    path('medication-history/', MedicationHistoryListView.as_view(),
         name='medication-history'),
    path('patient-list', PatientListView.as_view(), name='patients'),
    path('medication-changes/', MedicationChangesListView.as_view(), name='medication-changes'),
    path('analysis-of-clincal-problem/', AnalysisOfClinicalProblemListView.as_view(), name='analysis-of-cp'),
    
    
      # pharmcare create uris
    path('patient-create/', PatientDetailCreateView.as_view(), name='patient-create'),
    path('medication-history-create/', MedicationHistoryCreateView.as_view(),
         name='medication-history-create'),
    path('patients-create/', PatientCreateView.as_view(), name='patients-create'),
    path('medication-changes-create/', MedicationChangesCreateView.as_view(), name='medication-changes-create'),
    path('analysis-of-clincal-problem-create/', AnalysisOfClinicalProblemCreateView.as_view(), name='analysis-of-cp-create'),
    
    # pharmcare detail uris
    path('<str:slug>/', PatientDetailView.as_view(), name='patient-detail'),
    path('<int:pk>/', MedicationHistoryDetailView.as_view(),
         name='medication-history-detail'), 
    path('<str:slug>/', PatientsDetailView.as_view(), name='patients-detail'),
    path("<int:pk>/", MedicationChangesDetailView.as_view(), name='medication-changes-detail'),
    path("<str:slug>/", AnalysisOfClinicalProblemDetailView.as_view(), name='analysis-of-cp-detail'),

    
    # pharmcare update uris
    path('<str:slug>/patient-update/',
         UpdatePatientDetailView.as_view(), name='patient-update'),
    path('<int:pk>/medication-history-update/',
         MedicationHistoryUpdateView.as_view(), name='medication-history-update'),
    path('<str:slug>/patients-update/',
         PatientUpateView.as_view(), name='patients-update'),
    path("<int:pk>/update/", MedicationChangesUpdateView.as_view(), name='medication-changes-update'),
    path("<str:slug>/update/", AnalysisOfClinicalProblemUpdateView.as_view(), name='analysis-of-cp-update'),
    
    
   # pharmcare delete uris
    path('<str:slug>/patient-delete/',
         DeletePatientDetailView.as_view(), name='patient-delete'),

    path('<int:pk>/medication-history-delete/',
         MedicationHistoryDeleteView.as_view(), name='medication-history-delete'),
    
    path('<str:slug>/patients-delete/',
          PatientDeleteView.as_view(), name='patients-delete'),
         
    path("<int:pk>/delete/", MedicationChangesDeleteView.as_view(), name='medication-changes-delete'),
    path("<str:slug>/delete/", MedicationChangesDeleteView.as_view(), name='analysis-of-cp-delete'),

    # Patients URI - Many to Many field
    
]
