from django.contrib import admin
from tinymce.widgets import TinyMCE


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


# Register your models here.


admin.site.register(Patient)
admin.site.register(ProgressNote)
admin.site.register(MedicationChanges)
admin.site.register(PharmaceuticalCarePlan)
admin.site.register(AnalysisOfClinicalProblem)
admin.site.register(MonitoringPlan)
admin.site.register(FollowUpPlan)
admin.site.register(PatientDetail)
admin.site.register(MedicationHistory)


