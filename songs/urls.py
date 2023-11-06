from django.urls import path
from .views import (
    SongsByCategoryView,
    UnsubscribedView,
    CategoryListView,
    FooterView,
)
app_name = 'songs'

urlpatterns = [
    path('footer/', FooterView.as_view(), name='footer'),
   # path('<int:pk>/', UnsubscribedDetailView.as_view(), name='unsubscribe'),
    path('<int:pk>/', UnsubscribedView.as_view(), name='unsubscribe'),
    path('music_category_list/', CategoryListView.as_view(), name='category'),
    path('<str:slug>/', SongsByCategoryView.as_view(), name='song'),



]
