from django.contrib import admin
from .models import Lead, Agent, UserProfile


# Register your models here.

admin.site.register(Agent)
admin.site.register(UserProfile)
admin.site.register(Lead)
