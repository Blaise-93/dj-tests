from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from utils import (
    files,
    slug_modifier,

)
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


class AnalysisOfClinicalProblemListView(OrganizerPharmacistLoginRequiredMixin,
                                        ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the analysis of clinical problem of the patients in our
    db record."""

    template_name = 'pharmcare/analysis_of_cp/analysis-of-clinical-problem-list.html'
    ordering = 'id'

    context_object_name = 'analysis_of_cp'  # cp -> clinical problem

    def get(self, *args, **kwargs):

        query = self.request.GET.get('q', '')

        organization = self.request.user.userprofile
        user = self.request.user

        if query is None:
            messages.info(self.request,
                          files('pharmcare/mails/analysis-of-cp.txt'))
            return render(self.request, self.template_name)

        try:

            if user.is_organizer or user.is_pharmacist:

                self.queryset = AnalysisOfClinicalProblem.objects\
                    .filter(organization=organization)
            else:
                self.queryset = AnalysisOfClinicalProblem.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset = self.queryset.filter(
                Q(clinical_problem__icontains=query) |
                Q(priority__icontains=query) |
                Q(slug__icontains=query)
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
                'analysis_of_cp': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.success(
                self.request, 'Analysis of clinical problem form of the patient\
                was created successfully.')
        return reverse('pharmcare:analysis-of-cp')


class AnalysisOfClinicalProblemCreateView(OrganizerPharmacistLoginRequiredMixin,
                                          CreateView):
    """ View responsible to display patient's create 'analysis of clinical 
    problem'  records if the admin/pharmacists wants. """

    template_name = 'pharmcare/analysis_of_cp/analysis-of-clinical-problem-create.html'
    form_class = AnalysisOfClinicalProblemForm

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = AnalysisOfClinicalProblem.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = AnalysisOfClinicalProblem.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        user = self.request.user

        form = form.save(commit=False)
        form.user = user
        form.organization = user.userprofile
        form.slug = slug_modifier()
        # form.organization = user.pharmacist.organization
        form.save()

        return super(AnalysisOfClinicalProblemCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.success(
            self.request, 'Analysis of clinical problem form of the patient\
                was created successfully.')
        return reverse('pharmcare:analysis-of-cp')


class AnalysisOfClinicalProblemDetailView(OrganizerPharmacistLoginRequiredMixin,
                                          DetailView):
    """ View responsible to display patient's changes detai analysis of clinical 
    problem records if the admin/pharmacists wants. """

    template_name = 'pharmcare/analysis_of_cp/analysis-of-clinical-problem-detail.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                organization=organization)
        else:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


class AnalysisOfClinicalProblemUpdateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's analysis of clinical problem  
    records if the admin/pharmacists wants. """

    form_class = AnalysisOfClinicalProblemForm
    template_name = 'pharmcare/analysis_of_cp/analysis-of-clinical-problem-update.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                organization=organization)
        else:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Analysis of clinical problem form of the patient was updated successfully.')
        return reverse('pharmcare:analysis-of-cp')


class AnalysisOfClinicalProblemDeleteView(OrganizerPharmacistLoginRequiredMixin, DeleteView):
    """ View responsible to delete patient' analysis of clinical problem  records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/analysis_of_cp/analysis-of-clinical-problem-update.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                organization=organization)
        else:
            queryset = AnalysisOfClinicalProblem.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Analysis of clinical problem form of the patient was deleted successfully.')
        return reverse('pharmcare:analysis-of-cp')
