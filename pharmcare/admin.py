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
    FollowUpPlan


)


# Register your models here.\

class PatientDetailAdmin(admin.ModelAdmin):
    model = PatientDetail
    fields = ('patient_history', )
    widget = {
        'patient_history':admin_widgets.AdminTextareaWidget()
    }


admin.site.register(Patient)
admin.site.register(ProgressNote)
admin.site.register(MedicationChanges)
admin.site.register(PharmaceuticalCarePlan)
admin.site.register(AnalysisOfClinicalProblem)
admin.site.register(MonitoringPlan)
admin.site.register(FollowUpPlan)
admin.site.register(PatientDetail)
admin.site.register(MedicationHistory)
