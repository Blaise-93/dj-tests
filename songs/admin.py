from django.contrib import admin
from .models import Category, Song, User
from django.contrib.auth.admin import UserAdmin
from mptt.admin import DraggableMPTTAdmin


class CategoryAdmin(DraggableMPTTAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Song)
admin.site.register(User)
# admin.site.register(User, UserAdmin )
