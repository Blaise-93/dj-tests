from django.urls import path
from .views import (
    StaffListView,
    
    ManagementDetailView,
    ManagementListView,
    ManagementCreateView,
    ManagementDeleteView,
    ManagementUpdateView
)

app_name = 'staff'


urlpatterns = [
    path('', StaffListView.as_view(), name='attendance'),
   
    
    path('management/', ManagementListView.as_view(), name='management-list'), 
    path('management-create/', ManagementCreateView.as_view(), name='management-create'),
    path('management/<str:slug>/', ManagementDetailView.as_view(), name='management-detail'),
    path('management/<str:slug>/update/', ManagementUpdateView.as_view(), name='management-update'),
    path('management/<str:slug>/delete/', ManagementDeleteView.as_view(), name='management-delete'),
]
