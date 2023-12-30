from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
#from django.conf.urls.defaults import *
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView

)
from django.views.generic import TemplateView
from django.urls import path, include
from leads.views import LandingPageView, SignUpView

admin.site.site_header = 'MedConnect Pharmaceuticals'
admin.site.index_title = 'Django_Test Administration'


urlpatterns = [
    path('admin/', admin.site.urls),

    # Local apps
    path('', LandingPageView.as_view(), name='landing-page'),
    path('song/', include('songs.urls', namespace='songs')),
     path('accounts/', include('allauth.urls')),
    path('leads/', include("leads.urls", namespace='leads')),
    path("agents/", include("agents.urls", namespace='agents')),
    path('pharmcare/', include('pharmcare.urls', namespace='pharmcare')),
    path('chats/', include('chats.urls', namespace='chats')),
    path('staff-attendance/', include('staff.urls', namespace='staff')),



    # Registration URL - inherited for django.contrib.auths views
   # path('login/', LoginView.as_view(), name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    #path('signup/', SignUpView.as_view(), name='signup'),
    #path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    #path('password-reset-done/', PasswordResetDoneView.as_view(),
     #    name='password_reset_done'),
   # path('password-reset-confirm/<uidb64>/<token>/',
    #     PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('password-reset-complete/', PasswordResetCompleteView.as_view(),
     #    name='password_reset_complete'),


    # third party
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("__reload__/", include("django_browser_reload.urls")),


]


handler404 = 'pharmcare.views.patient_details.error_404'
handler500 =  'pharmcare.views.patient_details.error_500'
handler403 =  'pharmcare.views.patient_details.error_403'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
