from django.urls import path
from .views import (
    AgentListView,
    AgentCreateView,
    AgentDetailView, 
    AgentUpdateView, 
    AgentDeleteView
    )
app_name = 'agents'

urlpatterns = [
    path('', AgentListView.as_view(), name='agent-list'),
    path("agent-create/", AgentCreateView.as_view(), name="agent-create"),
    path('<str:slug>/', AgentDetailView.as_view(), name='agent-detail'), 
    path('<str:slug>/update/', AgentUpdateView.as_view(), name='agent-update'),
    path('<str:slug>/delete/', AgentDeleteView.as_view(), name='agent-delete')
]


