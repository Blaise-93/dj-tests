from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import (

    LeadsListView, LeadsDetailView,
    LeadsCreateView, LeadsUpdateView,
    LeadsDeleteView, AgentAssignedView,
    CategoryListView, CategoryDetailView,
    LeadCategoryUpdateView, CategoryCreateView,
     CategoryUpdateView, CategoryDeleteView


)


from .drf_views import (
    TestView,
    LeadCreateView,
    LeadUpdateView,
    LeadListView,
    LeadDeleteView,
    LeadRetrieveView

)


app_name = "leads"

urlpatterns = [

    path('', LeadsListView.as_view(), name="home-page"),
    path('categories/', CategoryListView.as_view(), name="category-list"),
    path('category-create/', CategoryCreateView.as_view(), name="category-create"),
    path("lead-create/", LeadsCreateView.as_view(), name="lead-create"),
    path("<str:slug>/", LeadsDetailView.as_view(), name="lead-detail"),
    path("<str:slug>/update/", LeadsUpdateView.as_view(), name="lead-update"), 
    path("<str:slug>/delete/", LeadsDeleteView.as_view(), name="lead-delete"),
    #"""  /leads/categories/contactedfk3k5w/update/ """,
   
   
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name="category-detail"), # /leads/rosayfuct0c/category/
    path( 'categories/<str:slug>/delete/', CategoryDeleteView.as_view(), name="category-delete"),
    path('categories/<str:slug>/update/', CategoryUpdateView.as_view(), name="category-update"),
   
    path("<str:slug>/category/",
         LeadCategoryUpdateView.as_view(), name="lead-category-update"),
    path("<str:slug>/assigned-agent/",
         AgentAssignedView.as_view(), name="assign-agent"),

    # API 
    path('drf_test/', TestView.as_view(), name="drf-test"),

    # DRF with Generic classes
    path('drf-test/', LeadListView.as_view(), name='drf-test'),
    path('create/', LeadCreateView.as_view(), name="create"),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name="delete"),
    path('<int:pk>/', LeadRetrieveView.as_view(), name="delete"),

    path('<int:pk>/delete/', LeadUpdateView.as_view(), name="delete"),



]


if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
