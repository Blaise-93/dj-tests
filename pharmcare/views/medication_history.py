from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utils import files
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


class MedicationHistoryListView(OrganizerPharmacistLoginRequiredMixin,
                                ListView):
    """ View responsible to display patient's medication history medication records 
    if the admin/pharmacists wants, and limit the list by 10 via pagination. """

    template_name = 'pharmcare/medication_history/medication-history-list.html'
    ordering = '-id'

    context_object_name = 'med_history'

    def get(self, *args, **kwargs):

        query = self.request.GET.get('q', '')

        organization = self.request.user.userprofile
        user = self.request.user

        # check for search query
        if query is None:
            messages.info(self.request,
                          files('/pharmcare/mails/medhistory.txt'))
            return render(self.request, self.template_name)

        try:

            if user.is_organizer or user.is_pharmacist:

                self.queryset = MedicationHistory.objects\
                    .filter(organization=organization)
            else:
                self.queryset = MedicationHistory.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset = self.queryset.filter(
                Q(medication_list__icontains=query) |
                Q(indication_and_evidence__icontains=query)
            )\
                .order_by('-id')

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
                'med_history': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:

            messages.info(self.request,
                          f"""Apologies, the patient medication history you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:medication-history')


class MedicationHistoryCreateView(OrganizerPharmacistLoginRequiredMixin,
                                  CreateView):
    """ View responsible to display patient's medication history create medication records 
    if the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_history/medication-history-create.html'
    form_class = MedicationHistoryForm

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationHistory.objects.filter(
                organization=organization)
        else:
            queryset = MedicationHistory.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def form_valid(self, form: BaseModelForm) -> HttpResponse:

        user = self.request.user

        form = form.save(commit=False)
        form.user = user
        form.organization = user.userprofile
        # form.organization = user.pharmacist.organization
        form.save()
        return super(MedicationHistoryCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.success(self.request,
                         "The patient's medication history was successfully created!")
        return reverse('pharmcare:medication-history')


class MedicationHistoryDetailView(OrganizerPharmacistLoginRequiredMixin,
                                  DetailView):
    """ View responsible to display patient's detail medication records 
    if the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_history/medication-history-detail.html'
    context_object_name = 'med_history'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationHistory.objects.filter(
                organization=organization)
        else:
            queryset = MedicationHistory.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


class MedicationHistoryUpdateView(OrganizerPharmacistLoginRequiredMixin,
                                  UpdateView):
    """ View responsible for updating patient's medication records if the
    admin/pharmacists wants. """
    form_class = MedicationHistoryForm
    template_name = 'pharmcare/medication_history/medication-history-update.html'
    context_object_name = 'med_history'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationHistory.objects.filter(
                organization=organization)
        else:
            queryset = MedicationHistory.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:
        messages.success(self.request,
                         "The patient's medication history was successfully updated!")
        return reverse('pharmcare:medication-history')


class MedicationHistoryDeleteView(OrganizerPharmacistLoginRequiredMixin,
                                  DeleteView):
    """ View responsible to delete patient's medication records if
    the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_history/medication-history-delete.html'
    context_object_name = 'med_history'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationHistory.objects.filter(
                organization=organization)
        else:
            queryset = MedicationHistory.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:
        messages.success(self.request,
                         "The patient's medication history was successfully deleted!")
        return reverse('pharmcare:medication-history')
