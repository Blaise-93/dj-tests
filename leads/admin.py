from django.contrib import admin
from tinymce.widgets import TinyMCE


from .models import (
    Lead, 
    Agent, 
    Category,
    UserProfile,
    Contact,
)

class AgentAdmin(admin.ModelAdmin):
    """ Customized agent admin class in our admin db  """
    list_display = [
        'user',
        'first_name',
        'last_name',
        'email',
        'slug',
        'organization',
         'date_joined',
    ]
    
    list_filter = ['first_name', 'email', 'user__username']

    search_fields = ['user__username', 'first_name']
    
    list_display_links = [
        'user',
        'email'
    ]
    
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name' ,
        'age', 
        'organization',
        'agent',
        'category',
        'social_media_accounts',
        'phoned',
        'phone_number',
        'description',
        'email',
        'address',
        'files',
    ]
    search_fields = [
        'first_name',
        'organization',
        'agent',
        'category',
        'email',
    ]
    list_filter = [
        'first_name',
        'organization',
        'agent',
        'category',
    ]

class CategoryAdmin(admin.ModelAdmin):
    """customized category admin """
 
    list_display = [
     'name',
     'organization',
     'slug'
    ]
    
    search_fields = [
        'organization',
       
    ]
    
    list_filter = [
      'name',
     'organization',
     'slug',
    ]


admin.site.register(Agent, AgentAdmin)
admin.site.register(UserProfile)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Category, CategoryAdmin )

    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """ Customized contact admin class in our admin db  """
    
    list_display = [
        'full_name',
        'email', 
        'country',
        'subject',
        'message',
        'user_ticket', 
        'date_created'
    ]
    
    list_filter = ['full_name', 'email', 'user_ticket']
    
    search_fields = [
        'full_name', 'email', 'user_ticket'
    ]
    
    
    



