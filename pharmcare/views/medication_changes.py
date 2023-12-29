from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utils import (
    files,
    utc_standard_time
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


class MedicationChangesListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request 
    cycle to display the medication changes of the patients in our db record.

    """

    template_name = 'pharmcare/medication_changes/medication-changes-list.html'
    ordering = 'id'

    context_object_name = 'med_changes'

    def get(self, *args, **kwargs):

        query = self.request.GET.get('q', '')

        organization = self.request.user.userprofile
        user = self.request.user

        # check for search query
        if query is None:
            messages.info(self.request,
                          files('/pharmcare/mails/medchanges.txt'))
            return render(self.request, self.template_name)

        try:

            if user.is_organizer or user.is_pharmacist:

                self.queryset = MedicationChanges.objects\
                    .filter(organization=organization)
            else:
                self.queryset = MedicationChanges.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset = self.queryset.filter(
                Q(dose__icontains=query) |
                Q(route__icontains=query)
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
                'med_changes': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:

            messages.info(self.request,
                          f"""Apologies, the patient medication changes you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:medication-changes')


class MedicationChangesCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View responsible to display patient's create medication changes
    records if the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_changes/medication-changes-create.html'
    form_class = MedicationChangesForm

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationChanges.objects.filter(
                organization=organization)
        else:
            queryset = MedicationChanges.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """ instantously create and save patient's slug and start_or_continued
        date to our db prior to saving every entry provided that form is
        valid."""

        user = self.request.user

        # instances to save when the form is called
        med_changes = form.save(commit=False)
        med_changes.user = user
        med_changes.organization = user.userprofile
        med_changes.start_or_continued_date = utc_standard_time().date()

        # med_changes.organization = user.pharmacist.organization
        med_changes.save()
        return super(MedicationChangesCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.success(
            self.request, 'Medication changes was created successfully.')
        return reverse('pharmcare:medication-changes')


class MedicationChangesDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ View responsible to display patient's changes detail medication records 
    if the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_changes/medication-changes-detail.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationChanges.objects.filter(
                organization=organization)
        else:
            queryset = MedicationChanges.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


class MedicationChangesUpdateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's medication changes records
    if the admin/pharmacists wants. """

    form_class = MedicationChangesForm
    template_name = 'pharmcare/medication_changes/medication-changes-update.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationChanges.objects.filter(
                organization=organization)
        else:
            queryset = MedicationChanges.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:
        messages.success(self.request,
                         "The patient's medication changes  was successfully updated!")
        return reverse('pharmcare:medication-changes')


class MedicationChangesDeleteView(OrganizerPharmacistLoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's medication changes records if
    the admin/pharmacists wants. """

    template_name = 'pharmcare/medication_changes/medication-history-delete.html'

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = MedicationChanges.objects.filter(
                organization=organization)
        else:
            queryset = MedicationChanges.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self) -> str:

        messages.success(
            "The patient's medication changes  was successfully deleted!")
        return reverse('pharmcare:medication-changes')
