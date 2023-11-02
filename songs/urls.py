from django.urls import path
from .views import SongsByCategoryView, CategoryListView
app_name = 'songs'

urlpatterns = [
    path('music_category_list/', CategoryListView.as_view(), name='category'),
    path('<str:slug>/', SongsByCategoryView.as_view(), name='song')
]
