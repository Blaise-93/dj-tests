from django.urls import path
from pharmcare.views.pharmacists import *

from pharmcare.views.patient_details import (
    PatientDetailListView,
    PatientDetailCreateView,
    PatientDetailView,
    UpdatePatientDetailView,
    DeletePatientDetailView,
)

from pharmcare.views.medication_history import (
    MedicationHistoryListView,
    MedicationHistoryCreateView,
    MedicationHistoryDeleteView,
    MedicationHistoryUpdateView,
    MedicationHistoryDetailView,
)

from pharmcare.views.medication_changes import (
    MedicationChangesListView,
    MedicationChangesCreateView,
    MedicationChangesDetailView,
    MedicationChangesUpdateView,
    MedicationChangesDeleteView,
)
from pharmcare.views.monitoring_plans import (

    MonitoringPlanListView,
    MonitoringPlanCreateView,
    MonitoringPlanDetailView,
    MonitoringPlanUpdateView,
    MonitoringPlanDeleteView,

)

from pharmcare.views.analysis_of_cp import (

    AnalysisOfClinicalProblemListView,
    AnalysisOfClinicalProblemCreateView,
    AnalysisOfClinicalProblemDetailView,
    AnalysisOfClinicalProblemUpdateView,
    AnalysisOfClinicalProblemDeleteView,

)

from pharmcare.views.pharmaceutical_care_plan import (
    PatientSummaryListView,
    PatientSummaryCreateView,
    delete_patient_summary,
    PatientSummaryDetailView,
    PatientSummaryUpateView,
    #  PatientSummaryDeleteView,
)

from pharmcare.views.progess_notes import (

    ProgressNoteListView,
    ProgressNoteCreateView,
    ProgressNoteDetailView,
    ProgressNoteUpdateView,
    ProgressNoteDeleteView,
)

from pharmcare.views.follow_up_plans import (

    FollowUpPlanListView,
    FollowUpPlanCreateView,
    FollowUpPlanDetailView,
    FollowUpPlanUpdateView,
    FollowUpPlanDeleteView,

)

from pharmcare.views.patients import (
    PatientListView,
    PatientCreateView,
    PatientUpateView,
    delete_patient_view,
    PatientsDetailView
)


app_name = 'pharmcare'

urlpatterns = [
    # Pharmcare URI

    # pharmcare list URIs
    path('', PatientDetailListView.as_view(), name='patient'),
    path('medication-history/', MedicationHistoryListView.as_view(),
         name='medication-history'),
    path('patient-info/', PatientListView.as_view(), name='patient-info'),
    path('patient-list/', PatientSummaryListView.as_view(), name='patients'),
    path('medication-changes/', MedicationChangesListView.as_view(),
         name='medication-changes'),
    path('analysis-of-clincal-problem/',
         AnalysisOfClinicalProblemListView.as_view(), name='analysis-of-cp'),
    path('monitoring-plan/', MonitoringPlanListView.as_view(),
         name='monitoring-plan'),
    path('follow-up-plan/', FollowUpPlanListView.as_view(), name='follow-up-plan'),
    path('progress-note/', ProgressNoteListView.as_view(), name='progress-notes'),


    path('pharmacist/', PharmacistListView.as_view(), name="pharmacist-list"),


    # pharmcare create uris
    path('patient-create/', PatientDetailCreateView.as_view(), name='patient-create'),
    path('patient-info-create/', PatientCreateView.as_view(),
         name='patients-info-create'),
    path('medication-history-create/', MedicationHistoryCreateView.as_view(),
         name='medication-history-create'),
    path('patients-create/',  PatientSummaryCreateView.as_view(),
         name='patients-create'),
    path('medication-changes-create/', MedicationChangesCreateView.as_view(),
         name='medication-changes-create'),
    path('analysis-of-clincal-problem-create/',
         AnalysisOfClinicalProblemCreateView.as_view(), name='analysis-of-cp-create'),
    path('monitoring-plan-create/', MonitoringPlanCreateView.as_view(),
         name='monitoring-plan-create'),
    path('follow-up-plan-create/', FollowUpPlanCreateView.as_view(),
         name='follow-up-plan-create'),
    path('progress-note-create/', ProgressNoteCreateView.as_view(),
         name='progress-note-create'),


    path('pharmacist-create/', PharmacistCreateView.as_view(),
         name="pharmacist-create"),

    # pharmcare detail uris


    path('<str:slug>/', PatientDetailView.as_view(), name='patient-detail'),
    path('patient-info/<int:pk>/', PatientsDetailView.as_view(),
         name='patients-info-detail'),
    path("medication-changes/<str:slug>/",
         MedicationChangesDetailView.as_view(), name='medication-changes-detail'),
    path('medication-history/<int:pk>/', MedicationHistoryDetailView.as_view(),
         name='medication-history-detail'),

    path("analysis-of-clincal-problem/<str:slug>/",
         AnalysisOfClinicalProblemDetailView.as_view(), name='analysis-of-cp-detail'),
    path('patient-list/<int:pk>/',
         PatientSummaryDetailView.as_view(), name='patients-detail'),

    path("monitoring-plan/<str:slug>/",
         MonitoringPlanDetailView.as_view(), name='monitoring-plan-detail'),
    path("follow-up-plan/<str:slug>/", FollowUpPlanDetailView.as_view(),
         name='follow-up-plan-detail'),
    path("progress-note/<str:slug>/", ProgressNoteDetailView.as_view(),
         name='progress-note-detail'),

    path("pharmacist/<str:slug>/", PharmacistDetailView.as_view(),
         name='pharmacist-detail'),

    # pharmcare update uris
    path('<str:slug>/patient-update/',
         UpdatePatientDetailView.as_view(), name='patient-update'),
    path('medication-history/<int:pk>/medication-history-update/',
         MedicationHistoryUpdateView.as_view(), name='medication-history-update'),
    path('patient-list/<int:pk>/patients-update/',
         PatientSummaryUpateView.as_view(), name='patients-update'),
    path('patient-info/<int:pk>/update/',
         PatientUpateView.as_view(), name='patients-info-update'),
    path("medication-changes/<str:slug>/update/",
         MedicationChangesUpdateView.as_view(), name='medication-changes-update'),
    path("analysis-of-clincal-problem/<str:slug>/update/",
         AnalysisOfClinicalProblemUpdateView.as_view(), name='analysis-of-cp-update'),
    path("monitoring-plan/<str:slug>/update/",
         MonitoringPlanUpdateView.as_view(), name='monitoring-plan-update'),
    path("follow-up-plan/<str:slug>/update/",
         FollowUpPlanUpdateView.as_view(), name='follow-up-plan-update'),
    path("progress-note/<str:slug>/update/",
         ProgressNoteUpdateView.as_view(), name='progress-note-update'),



    path("pharmacist/<str:slug>/update/", PharmacistUpdateView.as_view(),
         name='pharmacist-update'),


    # pharmcare delete uris
    path('<str:slug>/patient-delete/',
         DeletePatientDetailView.as_view(), name='patient-delete'),

    path('medication-history/<int:pk>/medication-history-delete/',
         MedicationHistoryDeleteView.as_view(), name='medication-history-delete'),

    path('patient-list/<int:pk>/patients-delete/',
         delete_patient_summary, name='patients-delete'),
    path('patients-info/<int:pk>/delete/',
         delete_patient_view, name='patient-info-delete'),

    path("medication-changes/<str:slug>/delete/",
         MedicationChangesDeleteView.as_view(), name='medication-changes-delete'),
    path("analysis-of-clincal-problem/<str:slug>/delete/",
         AnalysisOfClinicalProblemDeleteView.as_view(), name='analysis-of-cp-delete'),
    path("monitoring-plan/<str:slug>/delete/",
         MonitoringPlanDeleteView.as_view(), name='monitoring-plan-delete'),
    path("follow-up-plan/<str:slug>/delete/",
         FollowUpPlanDeleteView.as_view(), name='follow-up-plan-delete'),
    path("progress-note/<str:slug>/delete/",
         ProgressNoteDeleteView.as_view(), name='progress-note-delete'),



    path("pharmacist/<str:slug>/delete/", PharmacistDeleteView.as_view(),
         name='pharmacist-delete'),



]
