from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from leads.models import Agent
from django.core.mail import send_mail
from .forms import AgentModelForm
from .mixins import  OrgnizerAndLoginRequiredMixin


class AgentListView( OrgnizerAndLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent-list.html'
    context_object_name = 'agents'

    def get_queryset(self):
        user_userprofile = self.request.user.userprofile
        print(user_userprofile)

        # filter by request user organization - so that each won't see or
        # have access to every agent in other organization
        # except their respective organization
        return Agent.objects.filter(organization=user_userprofile)


class AgentCreateView( OrgnizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent-create.html'
    form_class = AgentModelForm
    queryset = Agent.objects.all()

    def get_success_url(self) -> str:
        return reverse('agents:agent-list')

    def form_valid(self, form):
        # call form.save()
        agent = form.save(commit=False)
        # get the userprofile from the authenticated user
        agent.organization = self.request.user.userprofile
        agent.save()

        send_mail(
            subject='Agent mail',
            message="Kindly login in to access your agent status",
            from_email="tests@blaise.com",
            recipient_list=["kenny@gmail", "ony@gmail.com"]
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView( OrgnizerAndLoginRequiredMixin, generic.DetailView):

    context_object_name = 'agent'
    template_name = 'agents/agent-detail.html'

    def get_queryset(self) -> QuerySet[Any]:
        userprofile = self.request.user.userprofile
        return Agent.objects.filter(organization=userprofile)


class AgentUpdateView( OrgnizerAndLoginRequiredMixin, generic.UpdateView):
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
        return reverse('agents:agent-detail')


class AgentDeleteView( OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent-delete.html'


    def get_queryset(self) -> QuerySet[Any]:
        userprofile = self.request.user.userprofile
        return Agent.objects.filter(organization=userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


""" Two types of users - Organizer (main superuser) and agent  """