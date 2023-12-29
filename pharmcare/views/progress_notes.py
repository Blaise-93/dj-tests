from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views import View
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


class ProgressNoteListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the progress note of the patients in our db record."""

    template_name = 'pharmcare/progress_notes/progress-note-list.html'
    ordering = 'id'

    context_object_name = 'progress_notes'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        organization = self.request.user.userprofile
        user = self.request.user

        if query is None:
            messages.info(self.request,
                          files('pharmcare/mails/progress-note.txt'))
            return render(self.request, self.template_name)

        try:
            if user.is_organizer or user.is_pharmacist:
                self.queryset = ProgressNote.objects\
                    .filter(organization=organization)
            else:
                self.queryset = ProgressNote.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset = self.queryset.filter(
                Q(notes__icontains=query) |
                Q(date_created__icontains=query)

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
                'progress_notes': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the patient progress note record you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:progress-notes')


class ProgressNoteCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View responsible to display patient's create progress note records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/progress_notes/progress-note-create.html'
    form_class = ProgressNoteForm

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = ProgressNote.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = ProgressNote.objects.filter(
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

        return super(ProgressNoteCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s progress note was created successfully.')
        return reverse('pharmcare:progress-notes')


class ProgressNoteDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ View responsible to display patient's progress note detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/progress_notes/progress-note-detail.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = ProgressNote.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = ProgressNote.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset


class ProgressNoteUpdateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's progress note records if the
    admin/pharmacists wants. """
    form_class = ProgressNoteForm
    template_name = 'pharmcare/progress_notes/progress-note-update.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = ProgressNote.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = ProgressNote.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:progress-notes')


class ProgressNoteDeleteView(OrganizerPharmacistLoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's progress note records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/progress_notes/progress-note-delete.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = ProgressNote.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = ProgressNote.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:progress-notes')
