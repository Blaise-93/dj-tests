from django.urls import path
from django.views.generic import TemplateView
from .views import (
    SongsByCategoryView,
     user_unsubscribed_newsletter,
    CategoryListView,
    FooterView,
    ContactView,
    newsletter
)
app_name = 'songs'

urlpatterns = [
    path('footer/', FooterView.as_view(), name='footer'),
    path('alert/',
         TemplateView.as_view(template_name='snippets/alert.html'), name='alert'),
       path('contact/', ContactView.as_view(), name="contact"),
    path('unsubscribed/',  user_unsubscribed_newsletter, name='unsubscribe'),
    path('newsletter/',  newsletter, name='newsletter'),
    path('music_category_list/', CategoryListView.as_view(), name='category'),
    path('<str:slug>/', SongsByCategoryView.as_view(), name='song'),

]
