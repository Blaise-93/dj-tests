from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from utils import files
from agents.mixins import OrganizerAgentLoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from pharmcare.models import *
from pharmcare.forms import *
from django.core.paginator import Paginator, EmptyPage


class P_Paginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                # return the last page
                return self.num_pages
            elif int(number) < 1:
                # return the first page
                return 1
            else:
                raise

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
    paginate_by = 6
    template_name = 'pharmcare/pharmcare-list.html'
    paginator_class = P_Paginator 

    def get_queryset(self) -> QuerySet[Any]:
        """ override the queryset via strictly checking if the user is
        a pharmacist (agent), and if yes, then the organizer, that's the
        admin will assign him to a patient to accord him/her the
        pharmaceutical care plan s/he needs."""

        user = self.request.user

        query = self.request.GET.get('q', '')
        if query is None:
            messages.info(self.request, files(
                '/pharmcare/mails/patient-list.txt'))
            return render(self.request, self.template_name)

        if user.is_organizer:
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=False)

        else:
            queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization, pharmacist__isnull=False)

            queryset = queryset.filter(pharamacist__user=self.request.user)

          #  print(queryset)

        return queryset.order_by(self.ordering).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(gender__icontains=query) |
            Q(age__icontains=query) |
            Q(email__icontains=query)

        ).distinct()

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
            
        # update the pagination of our queryset -> patientdetail model
            page = self.request.GET.get('page', 1)
            paginator = self.paginator_class(queryset, self.paginate_by)
            
            queryset = paginator.page(page)

            context.update({
                "unassigned_patients": queryset,
                'patients': queryset
            })
            
            # context['patients'] = queryset
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
        """ function that gets the specific queryset of the user for pharmacist/organization 
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


class MedicationHistoryListView(OrganizerAgentLoginRequiredMixin, ListView):
    template_name = 'pharmcare/medication-history-list.html'
    ordering = 'id'
    queryset = MedicationHistory.objects.all().order_by(ordering)
    paginate_by = 12
    context_object_name = 'med_history'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')
            if query is None:
                messages.info(self.request,
                              files('/pharmcare/mails/medhistory.txt'))
                return render(self.request, self.template_name)

            self.queryset = MedicationHistory.objects.filter(
                Q(medication_list__icontains=query) |
                Q(indication_and_evidence__icontains=query)

            ).distinct()

           # print(self.queryset)
        return self.queryset


class MedicationHistoryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'pharmcare/medication-history-create.html'
    form_class = MedicationHistoryForm
    queryset = MedicationHistory.objects.all()


class MedicationHistoryDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-detail.html'
    queryset = MedicationHistory.objects.all()


class MedicationHistoryUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's medication records if the
    admin/pharmacists wants. """
    form_class = MedicationHistoryForm
    template_name = 'pharmcare/medication-history-update.html'
    queryset = MedicationHistory.objects.all()
    context_object_name = 'medication-history'

    def get_success_url(self) -> str:
        return reverse('pharmcare:patient-medication-history')


class MedicationHistoryDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's medication records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-delete.html'
    queryset = MedicationHistory.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:patient-medication-history')


class MedicationChangesView(LoginRequiredMixin, ListView):

    pass


class AnalysisOfClinicalProblemView(LoginRequiredMixin, ListView):

    pass


class MonitoringPlanView(LoginRequiredMixin, ListView):

    pass


class FollowUpPlanView(LoginRequiredMixin, ListView):

    pass
