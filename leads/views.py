from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Agent
from django.contrib.auth.forms import PasswordResetForm
from .forms import LeadModelForm, LeadForm, CustomUserForm
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
            queryset = Lead.objects.filter(organization=user.userprofile)
        if self.request.is_agent:
            # filter according n reassign the queryset
            # which doesnt make multiple queryset in the db

            # filter the agent user via deep filter call (agent__user: filters the lead based on the agent
            # field where that agent has a user = self.request.user )
            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset


class LeadsCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):
    queryset = Lead.objects.all()
    template_name = 'leads/lead-create.html'
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):
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


class LeadsUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead-update.html"
    context_object_name = 'lead'
    form_class = LeadModelForm
    queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse('leads:home-page')


class LeadsDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/lead-delete.html'
    queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse('leads:home-page')
