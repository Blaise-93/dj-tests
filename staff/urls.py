from django.urls import path
from views.attendance import (
    AttendanceListView,
    AttendanceCreateView,
    AttendanceDetailView,
    AttendanceUpdateView,
    AttendanceDeleteView,
    
)

from views.management import (
    ManagementAssignedView,
    
    ManagementDetailView,
    ManagementListView,
    ManagementCreateView,
    ManagementDeleteView,
    ManagementUpdateView
)

app_name = 'staff'


urlpatterns = [
    # list uri - staff
    path('', AttendanceListView.as_view(), name='attendance'),
    path('management/', ManagementListView.as_view(), name='management-list'), 
    
    # create uri - staff
    path('attendance-create/', AttendanceCreateView.as_view(), name='attendance-create'),
    path('management-create/', ManagementCreateView.as_view(), name='management-create'),
    
    path('<str:slug>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('management/<str:slug>/', ManagementDetailView.as_view(), name='management-detail'),
    
    path('<str:slug>/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('management/<str:slug>/update/', ManagementUpdateView.as_view(), name='management-update'),
    
    path('<str:slug>/delete/', AttendanceDeleteView.as_view(), name='attendance-delete'),
    path('management/<str:slug>/delete/', ManagementDeleteView.as_view(), name='management-delete'),
   
    path('<str:slug>/assigned-management/', ManagementAssignedView.as_view(), name='assigned-management')
]
    
   
   

 
