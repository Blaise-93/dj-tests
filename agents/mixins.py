from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages


class OrgnizerAndLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an organizer."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_organizer:
            messages.info(
                request, "You are not an organizer, please you cannot access this information.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class OrganizerAgentLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an organizer or an agent or a pharmacist."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated  \
            or not request.user.is_agent or not request.user.is_pharmacist:
            messages.info(
                request, "You are not an organizer or agent, please you cannot access this information.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    

class OrganizerManagementLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an organizer or an agent or a pharmacist."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated  \
             or not request.user.is_management:
            messages.info(
                request, "You are not an organizer or agent, please you cannot access this information.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
