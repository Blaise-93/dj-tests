from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Agent
from django.contrib.auth.forms import PasswordResetForm
from .forms import LeadModelForm, AgentAssignedForm, LeadForm, CustomUserForm
from django.core.exceptions import ObjectDoesNotExist
from agents.mixins import OrgnizerAndLoginRequiredMixin


""" CRUD + L """

# Registration


class SignUpView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserForm

    def get_success_url(self):
        return reverse('login')


class LandingPageView(generic.TemplateView):
    template_name = "leads/landing-page.html"


class LeadsListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead-list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization, agent__isnull=False)
            # filter according n reassign the queryset
            # which doesnt make multiple queryset in the db

            # filter the agent user via deep filter call (agent__user: filters the lead based on the agent
            # field where that agent has a user == self.request.user )

           # filter agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split leads that have not been 
        assigned yet to an agent """
        
        context = super(LeadsListView, self).get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_organizer:
            # agent__isnull= True -> to check whether a foreign key is null.
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=True
                )
        
            context.update({
                  "unassigned_leads":queryset
            })
        
        return context

class LeadsCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):

    template_name = 'leads/lead-create.html'
    form_class = LeadModelForm

    def get_queryset(self):
        organization = self.request.user.userprofile
        queryset = Lead.objects.filter(organization=organization, organization__isnull=True)
        return queryset

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):

        user = form.save(commit=False)
        # create lead user - organizer 
        user.is_agent = False
        user.is_organizer = True
        user.save()

        # create the agent from the form we saved
        Lead.objects.create(
            organization=self.request.user.userprofile
        )

        # TODO send email
        send_mail(
            subject='A lead has been created',
            message='Go to the site to see the new lead',
            from_email='blaise@gmail.com',
            recipient_list=['test2@gmail.com']
        )
        return super(LeadsCreateView, self).form_valid(form)


class LeadsDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):
    queryset = Lead.objects.all()
    template_name = "leads/lead-detail.html"

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)

            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset


class LeadsUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead-update.html"
    context_object_name = 'lead'
    form_class = LeadModelForm
    queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse('leads:home-page')

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            return Lead.objects.filter(organization=user.userprofile)


class LeadsDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/lead-delete.html'

    def get_queryset(self):
        user = self.request.user
        # initial queryset for entire organization?
        queryset = Lead.objects.filter(organization=user.userprofile)

        return queryset

    def get_success_url(self):
        return reverse('leads:home-page')


class AgentAssignedView(OrgnizerAndLoginRequiredMixin,generic.FormView):
    template_name = 'agents/agent-assigned.html'
    form_class = AgentAssignedForm
    
    def get_form_kwargs(self):
        return {'request': self.request } 
        
        
    def get_success_url(self):
        return reverse('leads:home-page')
    
    
    def form_valid(self, form):
        
        return super(AgentAssignedView, self).form_valid(form)
        

        
    
    
        
        
        
