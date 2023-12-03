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
    Team


)


# Register your models here.\

class PatientDetailAdmin(admin.ModelAdmin):
    model = PatientDetail
    fields = ('patient_history', )
    widget = {
        'patient_history':admin_widgets.AdminTextareaWidget()
    }

class TeamAdmin(admin.ModelAdmin):
    list_display = [
            'full_name',
            'position',
            'image',
            #'description',
            'alt_description',
            'facebook_aria_label',
            'twitter_aria_label',
            'instagram_aria_label',
            'facebook_link',
            'instagram_link',
            'twitter_link' ,
            'chat',
    ]

    search_fields = ["full_name", "position"]

admin.site.register(Patient)
admin.site.register(ProgressNote)
admin.site.register(MedicationChanges)
admin.site.register(PharmaceuticalCarePlan)
admin.site.register(AnalysisOfClinicalProblem)
admin.site.register(MonitoringPlan)
admin.site.register(FollowUpPlan)
admin.site.register(PatientDetail)
admin.site.register(MedicationHistory)
admin.site.register(Team, TeamAdmin)
