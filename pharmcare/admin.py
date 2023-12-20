from django.contrib import admin
from tinymce.widgets import TinyMCE
from tinymce.widgets import admin_widgets



from .models import (
    PharmaceuticalCarePlan,
    Patient,
    PatientDetail,
    ProgressNote,
    MedicationHistory,
    MedicationChanges,
    AnalysisOfClinicalProblem,
    MonitoringPlan,
    FollowUpPlan,
    Team,
    Pharmacist


)


class PatientDetailModelAdmin(admin.ModelAdmin):
    """ A class model admin that modifies/overide the admin panel of patient detail """
    model = PatientDetail
    fields = (
               'first_name',
        'last_name',
        'email',
        'marital_status',
        'patient_class',
        'age',
        "weight",
        'gender',
        'height',
        'patient_history',
        'past_medical_history',
        'social_history',
        'slug',
        'phone_number',
        'consultation')
    widget = {
        'patient_history': admin_widgets.AdminTextareaWidget(),
        'past_medical_history': admin_widgets.AdminTextareaWidget()
    }
    
    list_per_page = 10

    list_display = [
        'first_name',
        'last_name',
        'email',
        'marital_status',
        'patient_class',
        'age',
        "weight",
        'gender',
        'height',
        'patient_history',
        'past_medical_history',
        'social_history',
        'slug',
        'phone_number',
        'consultation'
    ]

    list_per_page = 10

    list_filter = [
        'first_name',
        'last_name',
        'slug',
        'email',
        'phone_number',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'gender',
        'phone_number',
    ]


class ProgressNoteModelAdmin(admin.ModelAdmin):
    """ A class model admin that modifies/overide the admin panel of progress note
    for our patient"""
    model = ProgressNote
    fields = ('notes', )

    list_per_page = 10
    
    list_display = [
        'notes',
        'slug',
        'date_created'
    ]

    list_per_page = 10

    search_fields = [
        'slug',

    ]


class MedicationHistoryModelAdmin(admin.ModelAdmin):
    """ A class model admin that modifies/overide the admin panel of medication history 
    for our patient"""
    model = MedicationHistory
    fields = ('medication_list', )
    widget = {
        'medication_list': admin_widgets.AdminTextareaWidget()
    }

    list_display = [
        'medication_list',
        'indication_and_evidence',
        'slug'
    ]

    list_per_page = 10

    search_fields = [
        'slug',

    ]


class MedicationChangesModelAdmin(admin.ModelAdmin):
    """ An admin class that modifies/override the medication change admin on how
    we want our patient information based on their respective medication to be
    rendered, like list display and the rest."""
    model = MedicationChanges
    fields = ('route', 'frequency')
    widget = {
        'indication': admin_widgets.AdminTextareaWidget()
    }

    list_display = [
        'medication_list',
        'dose',
        'frequency',
        'route',
        'indication',
        'stop_date',
    ]

    list_per_page = 10

    list_filter = [
        'route',
        'dose'
    ]

    search_fields = [
        'route',
        'dose'
    ]


class AnalysisOfClinicalProblemModelAdmin(admin.ModelAdmin):
    """ An admin class that modifies/override the analysis of clinical problem admin"""
    model = AnalysisOfClinicalProblem

    list_display = [
        "clinical_problem",
        "assessment",
        "priority",
        'slug',
        "action_taken_or_future_plan",
    ]

    list_per_page = 10

    search_fields = [
        'slug',
        "priority",
    ]


class MonitoringPlanModelAdmin(admin.ModelAdmin):
    """ A class that modifies/override admin class of monitoring plan of our patients
    to help us and prepolulate patient's monitoring plan fields like list display 
    in a nicer format etc."""
    model = MonitoringPlan
    fields = ('parameter_used', )

    list_display = (
        'parameter_used',
        'justification',
        'frequency',
        'results_and_action_plan',
        'slug',
        'date_created',
    )

    list_per_page = 10

    list_filter = [
        'parameter_used',
        'frequency',
        'slug',
    ]

    search_fields = [
        'parameter_used',
        'frequency',
        'slug',
    ]


class FollowUpPlanModelAdmin(admin.ModelAdmin):
    """ A class that modifies/override admin class of follow_up_plan of our patients
    to help us and prepolulate patient's follow up plan fields like list display 
    in a nicer format etc."""
    model = FollowUpPlan

    list_display = [
        'follow_up_requirement',
        'action_taken_and_future_plan',
        'state_of_improvement_by_score',
        'has_improved_than_before',
        'adhered_to_medications_given',
        'referral',
        'date_created'
    ]

    list_per_page = 10

    list_filter = [
        'has_improved_than_before',
        'adhered_to_medications_given',
        'referral'
    ]

    search_fields = [
        'has_improved_than_before',
        'adhered_to_medications_given',
        'referral'
    ]


class PatientModelAdmin(admin.ModelAdmin):
    """ A class that modifies/override admin class of patient model of our patients
    to help us and prepolulate patient's patients' fields like list display 
    in a nicer format etc."""
    model = Patient

    list_display = [
        'medical_charge',
        'notes',
        'patient',
        'medical_history',
        'total',
        'date_created'
    ]

    list_per_page = 10

    list_filter = [
        'medical_charge',
        'total'
    ]

    search_fields = [
        'medical_charge',
        'patient__first_name'
        'slug',
    ]


class PharmaceuticalPlanModelAdmin(admin.ModelAdmin):
    """ A class that modifies/override admin class of Pharmaceutical plan of our patients
    to help us and prepolulate patient's monitoring plan fields like list display 
    in a nicer format etc."""
    model = PharmaceuticalCarePlan
    
    def get_patient_name(self, request) -> str:
        
        patient_list = PharmaceuticalCarePlan.objects.get(user=request.user)
        
        for patient_name in patient_list.patients.all():
            return patient_name
    
    list_display = [
        'user',
        'patient_unique_code',
        'has_improved',
        'progress_note',
        'medication_changes',
        'pharmacist',
        'analysis_of_clinical_problem',
        'date_created',
        
       
    ]
    
   
    list_per_page = 10

    list_filter = [
        'user__username',
        'patient_unique_code', 
        'has_improved',
    ]

    search_fields = [
        'user__username',
        'patient_unique_code',
        'has_improved',
    ]


admin.site.register(PatientDetail, PatientDetailModelAdmin)
admin.site.register(MedicationHistory, MedicationHistoryModelAdmin)
admin.site.register(Patient, PatientModelAdmin)
admin.site.register(ProgressNote, ProgressNoteModelAdmin)
admin.site.register(MedicationChanges, MedicationChangesModelAdmin)
admin.site.register(AnalysisOfClinicalProblem,
                    AnalysisOfClinicalProblemModelAdmin)
admin.site.register(MonitoringPlan, MonitoringPlanModelAdmin)
admin.site.register(FollowUpPlan, FollowUpPlanModelAdmin)
admin.site.register(PharmaceuticalCarePlan, PharmaceuticalPlanModelAdmin)


admin.site.register(Pharmacist) #TODO - work on customizing it's admin

@admin.register(Team)
class TeamModelAdmin(admin.ModelAdmin):

    list_display = [
        'full_name',
        'position',
        'image',
        'alt_description',
        'facebook_aria_label',
        'twitter_aria_label',
        'instagram_aria_label',
        'facebook_link',
        'instagram_link',
        'twitter_link',
        'chat',
    ]

    search_fields = ["full_name", "position"]
