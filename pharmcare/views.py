from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    DeleteView,
    UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from pharmcare.models import *
from pharmcare.forms import *


class PatientListView(LoginRequiredMixin, ListView):
    """ Patient view class: display the model data as a request made by the client
    on the server when needed.

    Important information:

    Please note that agent and pharmacist are used interchangeable. However, for the 
    context, it is better we use pharmacist here.
    """
   # queryset = Patient.objects.all()
    ordering = 'id'
    context_object_name = 'patients'
    paginate_by = 12
    template_name = 'pharmcare/pharmcare-list.html'

    def get_queryset(self) -> QuerySet[Any]:
        """ override the queryset via strictly checking if the user is
        a pharmacist (agent), and if yes, then the organizer, that's the
        admin will assign him to a patient to accord him/her the
        pharmaceutical care plan s/he needs."""

        user = self.request.user
        if user.is_organizer:
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=False)
        else:
            queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization, pharmacist__isnull=False)

            queryset = queryset.filter(pharamacist__user=self.request.user)

        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split patients that have not been 
        assigned yet to an agent """

        context = super(PatientListView, self).get_context_data()
        user = self.request.user

        if user.is_organizer:
            # agent__isnull= True -> to check whether a foreign key is null.
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=True
            )

            context.update({
                "unassigned_patients": queryset
            })

          #  print(context['unassigned_patients'])

        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    """ View that handles creating a patient details in our database by the 
    assigned pharmacists or the admin."""

    template_name = 'pharmcare/pharmcare-create.html'
    form_class = PatientDetailForm
    context_object_name = 'patient'

    def get_queryset(self):
        """  Since, it is rare to see a community pharmacy or hospital not managed by
        a pharmacists according the law of most countries in the world, I think it is appropriate to 
        give pharmacists acting as agents permissions to collect and create patient data
        in the database. This is a 50:50 win situation by the organization because it is
        quite inconvenient for each patient data collection he/she will be the one that
        would assign the patient to a specific pharmacist in the organization or the branch"""

        organization = self.request.user.userprofile
        pharmacist = self.request.user
        if organization:
            queryset = PatientDetail.objects.filter(
                organization=organization)
        else:
            queryset = PatientDetail.objects.filter(
                pharmacist=pharmacist.organization
            )
            queryset = queryset.filter(pharamacist__user=pharmacist)

        return queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:patient')

    def form_valid(self, form):

        # fetch and save organization or pharmacist id in our db
        patient = form.save(commit=False)
        if self.request.user.userprofile:
            patient.organization = self.request.user.userprofile
            patient.save()
        else:
            patient.pharmacist = self.request.user.pharmacist.organization
            patient.save()

        messages.info(
            self.request, f'Patient medical details was created successfully.')
        return super(PatientCreateView, self).form_valid(form)


class PatientDetailView(LoginRequiredMixin, DetailView):
    """ This class shows the pharmacist/organization a detailed information of the 
    patient extracted from pharmcare_patientdetail table.
    """
    template_name = "pharmcare/pharmcare-detail.html"
    # queryset = PatientDetail.objects.all()

    def get_queryset(self):
        """  get the specific queryset of the user for pharmacist/organization 
        to view for further records. """
        organization = self.request.user
        pharmacist = self.request.user
        if organization.is_organizer:
            queryset = PatientDetail.objects.filter(
                organization=organization.userprofile)
        else:
            queryset = PatientDetail.objects.filter(
                organization=pharmacist.organization
            )
            queryset = queryset.filter(pharamacist__user=pharmacist)

        return queryset


class UpdatePatientDetailView(LoginRequiredMixin, UpdateView):
    """ View that handles users (pharmacists/organization) requests to
    update the form input of our registered patients."""

    template_name = 'pharmcare/pharmcare-update.html'
    form_class = PatientDetailForm
    context_object_name = 'patient'

    def get_queryset(self):
        """  get the specific queryset of the user for pharmacist/organization 
        to view for further records. """

        organization = self.request.user
        pharmacist = self.request.user
        if organization.is_organizer:
            queryset = PatientDetail.objects.filter(
                organization=organization.userprofile)
        else:
            queryset = PatientDetail.objects.filter(
                organization=pharmacist.organization
            )
            queryset = queryset.filter(pharamacist__user=pharmacist)

        return queryset
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        patient_first_name = form.cleaned_data['first_name']
        patient_last_name = form.cleaned_data['last_name']
        messages.info(self.request, 
            f'{patient_first_name} {patient_last_name} data was successfully updated! ')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pharmcare:patient')


class DeletePatientView(LoginRequiredMixin, DeleteView):
    template_name = 'pharmcare/pharmcare-delete.html'

    def get_queryset(self):
        """  get the specific queryset of the user for pharmacist/organization 
        to view for further records. """

        organization = self.request.user
        pharmacist = self.request.user
        if organization.is_organizer:
            queryset = PatientDetail.objects.filter(
                organization=organization.userprofile)
        else:
            queryset = PatientDetail.objects.filter(
                organization=pharmacist.organization
            )
            queryset = queryset.filter(pharamacist__user=pharmacist)

        return queryset
      
    def get_success_url(self):
        return reverse("pharmcare:patient")