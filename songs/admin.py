from django.contrib import admin
from .models import Category,User, SubscribedUsers
from django.contrib.auth.admin import UserAdmin
from mptt.admin import DraggableMPTTAdmin


#class CategoryAdmin(DraggableMPTTAdmin):
    # pass


#admin.site.register(Category, CategoryAdmin)
#admin.site.register(Song)

admin.site.register(User)
admin.site.register(SubscribedUsers)

# admin.site.register(User, UserAdmin )
