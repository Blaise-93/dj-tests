from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    
    
    )
from django.views.generic import TemplateView
from django.urls import path, include
from leads.views import  LandingPageView, SignUpView

admin.site.site_header = 'Django_Test Enterprise'
admin.site.index_title = 'Django_Test Administration'



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    #path('', landing_page, name="landing-page"),
    path('', LandingPageView.as_view(), name='landing-page'),
    path('song/', include('songs.urls', namespace='songs')),
    path('leads/', include("leads.urls", namespace='leads')),
    path("__reload__/", include("django_browser_reload.urls")),
    path("agents/", include("agents.urls", namespace='agents')),
    
    # Registra tion URL
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    



]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
