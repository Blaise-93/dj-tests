from django.contrib import admin
from tinymce.widgets import TinyMCE


from .models import (
    Lead, 
    Agent, 
    Category,
    UserProfile,

    
    
)


# Register your models here.

admin.site.register(Agent)
admin.site.register(UserProfile)
admin.site.register(Lead)
admin.site.register(Category)

