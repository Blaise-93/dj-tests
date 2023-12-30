from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from agents.mixins import OrganizerPharmacistLoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView)
from pharmcare.models import *
from pharmcare.forms import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class MonitoringPlanListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the monitoring plan of the patients in our db record."""
    template_name = 'pharmcare/monitoring_plans/monitoring-plan-list.html'
    ordering = 'id'

    has_improved = models.BooleanField(default=False)

    context_object_name = 'monitoring_plan'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        organization = self.request.user.userprofile
        user = self.request.user

        try:
            if user.is_organizer or user.is_pharmacist:
                self.queryset = MonitoringPlan.objects\
                    .filter(organization=organization)
            else:
                self.queryset = MonitoringPlan.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset =  self.queryset.filter(
                    Q(frequency__icontains=query) |
                    Q(parameter_used__icontains=query)

                )\
                    .order_by('id')

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)

            context = {
                'monitoring_plan': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the patient monitoring record you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:monitoring-plan')


class MonitoringPlanCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View responsible to display patient's create  monitoring plan records 
    if the admin/pharmacists wants. """

    template_name = 'pharmcare/monitoring_plans/monitoring-plan-create.html'
    form_class = MonitoringPlanForm
   # queryset = MonitoringPlan.objects.all()

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        user = self.request.user

        form = form.save(commit=False)
        form.user = user
        form.organization = user.userprofile
        # form.organization = user.pharmacist.organization
        form.save()

        return super(MonitoringPlanCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s monitoring plan was created successfully.')
        return reverse('pharmcare:monitoring-plan')

    """ 
    def form_valid(self, form):
        form = form.save(commit=False)
        form.slug = slug_modifier()
        form.save()
        return super(MonitoringPlanCreateView, self).form_valid(form) """


class MonitoringPlanDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ View responsible to display patient's  monitoring plan detail
    medication records if the admin/pharmacists wants. """

    template_name = 'pharmcare/monitoring_plans/monitoring-plan-detail.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset


class MonitoringPlanUpdateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's  monitoring plan records if the
    admin/pharmacists wants. """

    form_class = MonitoringPlanForm
    template_name = 'pharmcare/monitoring_plans/monitoring-plan-update.html'
   # queryset = MonitoringPlan.objects.all()

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:monitoring-plan')


class MonitoringPlanDeleteView(OrganizerPharmacistLoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's  monitoring plan records if
    the admin/pharmacists wants. """

    template_name = 'pharmcare/monitoring_plans/monitoring-plan-delete.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = MonitoringPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:monitoring-plan')
