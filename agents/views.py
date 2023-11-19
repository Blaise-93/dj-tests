from typing import Any
from django.db.models.query import QuerySet
from django.urls import reverse
from django.views import generic
from leads.models import Agent
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from utils import password_setter, files
from .forms import AgentModelForm
from .mixins import OrgnizerAndLoginRequiredMixin

class AgentListView(OrgnizerAndLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent-list.html'
    context_object_name = 'agents'

    def get_queryset(self):
        user_userprofile = self.request.user.userprofile
       

        # filter by request user organization - so that each won't see or
        # have access to every agent in other organization
        # except their respective organization
        return Agent.objects.filter(organization=user_userprofile)


class AgentCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent-create.html'
    form_class = AgentModelForm
    queryset = Agent.objects.all()

    def get_success_url(self) -> str:
        return reverse('agents:agent-list')

    def form_valid(self, form):
        # call form.save()
        user = form.save(commit=False)
        # create agent user
        user.is_agent = True
        user.is_organizer = False
        # set password
        user.set_password(password_setter())
        user.save()

        email = form.cleaned_data.get('email')
        # create the agent from the form we saved
        Agent.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        
        send_mail(
            subject='You are invited to be an agent in our organization',
            message=files('agents/mails/agent-request-mail.txt'),
            from_email="tests@blaise.com",
            recipient_list=[email, ]
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):

    context_object_name = 'agent'
    template_name = 'agents/agent-detail.html'

    def get_queryset(self) -> QuerySet[Any]:
        userprofile = self.request.user.userprofile
        return Agent.objects.filter(organization=userprofile)

    def get_success_url(self):

        return reverse('agents:agent-detail')


class AgentUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent-update.html"
    context_object_name = 'agent'
    form_class = AgentModelForm

    def get_queryset(self) -> QuerySet[Any]:
        """ This function get the user profile queryset. Since we don't want agent to update
        information that belongs to other agents in another organization which s/he does not 
        manage. 
            """
        userprofile = self.request.user.userprofile
        return Agent.objects.filter(organization=userprofile)

    def get_success_url(self):
        return reverse('leads:home-page')


class AgentDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent-delete.html'

    def get_queryset(self) -> QuerySet[Any]:
        userprofile = self.request.user.userprofile
        return Agent.objects.filter(organization=userprofile)

    def get_success_url(self):
        return reverse("leads:home-page")


""" Two types of users - Organizer (main superuser) and agent  """
