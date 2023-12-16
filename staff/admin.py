from django.contrib import admin
from staff.models import Attendance, Management

class AttendanceModelAdmin(admin.ModelAdmin):
    list_display = [
            'full_name',
            'sign_in_time',
            'sign_out_time',
            'date_added',
            'staff_attendance_ref',
            'organization' ,
            'management', 
            'date_sign_out_time',
            'date_created'
    ]
    list_filter = [
          'full_name',
    ]

    list_per_page = 10
    
    search_fields = [
          'full_name',
           'staff_attendance_ref',
    ]
    
    

admin.site.register(Attendance, AttendanceModelAdmin)
admin.site.register(Management)