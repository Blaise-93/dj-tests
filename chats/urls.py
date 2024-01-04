from django.urls import path
from .views import ChatView

app_name = 'chats'

urlpatterns = [
    path('', ChatView.as_view(), name='chats')
]


