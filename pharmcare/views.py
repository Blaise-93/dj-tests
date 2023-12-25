from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utils import (
    files,
    slug_modifier,
    utc_standard_time
)
from django.contrib.auth.decorators import login_required
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


# ERROR HANDLERS
def error_404(request, exception):
    """ handles 404 exception neatly using our 404 template """

    return render(request, "snippets/404.html", status=404)


def error_500(request):
    """"
    Handles HTTP 500 errors
    """
    return render(request, 'snippets/500.html', status=500)


def error_403(request, exception):
    """"
    Handles HTTP 403 errors - the server understood the request,
    but it is forbidden
    """
    return render(request, 'snippets/403.html', status=403)


# PHARMACIST VIEW -> Checkout views_extension.py where the
# business logics are created


# PHARMACEUTICAL CARE PLAN
class PatientDetailListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ Patient Detail View class: display the model data as a request made by 
    the client on the server when needed.
    """

    ordering = 'first_name'
    context_object_name = 'patients'
    template_name = 'pharmcare/pharmcare-list.html'

    def get_queryset(self) -> QuerySet[Any]:
        """ override the queryset via strictly checking if the user is
        a pharmacist, and if yes, then the organizer, that's the
        admin will assign him to a patient to accord him/her the
        pharmaceutical care plan s/he needs."""

        user = self.request.user

        query = self.request.GET.get('q', '')
        if query is None:
            messages.info(self.request, files(
                '/pharmcare/mails/patient-list.txt'))
            return render(self.request, self.template_name)

        if user.is_organizer or user.is_pharmacist:
            self.queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=True)

           # print(user.userprofile)
        else:
            self.queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization,
                pharmacist__isnull=True
            )
            print(user.pharmacist.organization)

            self.queryset = PatientDetail.objects.filter(
                pharmacist__user=user, pharmacist__isnull=True)
            print(self.queryset)

        self.queryset = self.queryset.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(gender__icontains=query)

        ).distinct()

        # Paginate Pharmcare list
        search = Paginator(self.queryset, 10)
        page = self.request.GET.get('page')

        try:
            self.queryset = search.get_page(page)

        except PageNotAnInteger:
            self.queryset = search.get_page(1)

        except EmptyPage:
            self.queryset = search.get_page(search.num_pages)

        return self.queryset

    def get_success_url(self):

        return reverse('landing-page')


class PatientDetailCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View that handles creating a patient details in our database by the 
    assigned pharmacists or the admin."""

    template_name = 'pharmcare/pharmcare-create.html'
    form_class = PatientDetailModelForm
    context_object_name = 'patient'

    def get_queryset(self):
        """  Since, it is rare to see a community pharmacy or hospital not
        managed by a pharmacists according to the law of most countries in the
        world, I think it is appropriate to give pharmacists
        permissions to collect and create patient data in the database. 
        This is a 50:50 win situation by the organization because it is
        quite inconvenient for each patient data collection he/she will be
        the one that would assign the patient to a specific pharmacist in
        the organization or the branch"""

        organization = self.request.user.userprofile
        user = self.request.user

        if user.is_organizer or user.is_pharmacist:
            queryset = PatientDetail.objects.filter(
                organization=organization,  organization__isnull=True)
        else:
            queryset = PatientDetail.objects.filter(
                pharmacist=user.pharmacist.organization, pharmacist__isnull=True
            )
            queryset = queryset.filter(
                pharmacist__user=user, pharmacist__isnull=True)

        return queryset

    def get_success_url(self) -> str:
        messages.success(
            self.request, f'Patient medical details was created successfully. Thank you!')
        return reverse('pharmcare:patient')

    def form_valid(self, form):

        # fetch and save organization or pharmacist id in our db
        patient_detail = form.save(commit=False)

        if patient_detail.pharmacist:
            patient_detail.pharmacist = self.request.user.pharmacist.organization
            patient_detail.save()
        else:
            patient_detail.organization = self.request.user.userprofile
            patient_detail.save()

        return super(PatientDetailCreateView, self).form_valid(form)


class PatientDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ This class shows the pharmacist/organization a detailed information of
    the patient extracted from pharmcare_patientdetail table.
    """
    template_name = "pharmcare/pharmcare-detail.html"
    # queryset = PatientDetail.objects.all()

    def get_queryset(self):
        """  get the specific queryset of the user for pharmacist/organization 
        to view for further records. """
        user = self.request.user

        if user.is_organizer or user.is_pharmacist:
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile)
        else:

            queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


class UpdatePatientDetailView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View that handles users (pharmacists/organization) requests to
    update the form input of our registered patients."""

    template_name = 'pharmcare/pharmcare-update.html'
    form_class = PatientDetailModelForm
    context_object_name = 'patient'

    def get_queryset(self):
        """ function that gets the specific queryset of the user for 
        pharmacist/organization to view for further records. """

        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile)
        else:
            queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def form_valid(self, form: BaseModelForm) -> HttpResponse:

        # fetch the first_name and last_name that has been saved
        patient_first_name = form.cleaned_data['first_name']
        patient_last_name = form.cleaned_data['last_name']
        form = form.save(commit=False)
        form.date_created = utc_standard_time()
        form.save()
        messages.info(self.request,
                      f'{patient_first_name} {patient_last_name}\
                data was successfully updated! ')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pharmcare:patient')


class DeletePatientDetailView(OrganizerPharmacistLoginRequiredMixin,
                              DeleteView):
    """ Handles all the delete entry request made by the registered user """
    template_name = 'pharmcare/pharmcare-delete.html'

    def get_queryset(self):
        """  get the specific queryset of the user for pharmacist/organization 
        to view for further records. """

        user = self.request.user

        if user.is_organizer or user.is_pharmacist:
            queryset = PatientDetail.objects.filter(
                organization=user.userprofile)
        else:
            queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset

    def get_success_url(self):
        return reverse("pharmcare:patient")


class MedicationHistoryListView(OrganizerPharmacistLoginRequiredMixin,
                                ListView):
    """ View responsible to display patient's medication history medication records 
    if the admin/pharmacists wants, and limit the list by 10 via pagination. """

    template_name = 'pharmcare/medication-history-list.html'
    ordering = 'id'

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
                self.queryset.filter(
               Q(medication_list__icontains=query) |
                Q(indication_and_evidence__icontains=query)
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

    template_name = 'pharmcare/medication-history-create.html'
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

    template_name = 'pharmcare/medication-history-detail.html'
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
    template_name = 'pharmcare/medication-history-update.html'
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

    template_name = 'pharmcare/medication-history-delete.html'
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


class MedicationChangesListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request 
    cycle to display the medication changes of the patients in our db record.

    """

    template_name = 'pharmcare/medication-changes-list.html'
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
                self.queryset.filter(
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

    template_name = 'pharmcare/medication-changes-create.html'
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

    template_name = 'pharmcare/medication-changes-detail.html'

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
    template_name = 'pharmcare/medication-changes-update.html'

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

    template_name = 'pharmcare/medication-history-delete.html'

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


class AnalysisOfClinicalProblemListView(OrganizerPharmacistLoginRequiredMixin,
                                        ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the analysis of clinical problem of the patients in our
    db record."""

    template_name = 'pharmcare/analysis-of-clinical-problem-list.html'
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
                self.queryset.filter(
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

    template_name = 'pharmcare/analysis-of-clinical-problem-create.html'
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

    template_name = 'pharmcare/analysis-of-clinical-problem-detail.html'

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
    template_name = 'pharmcare/analysis-of-clinical-problem-update.html'

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
    template_name = 'pharmcare/analysis-of-clinical-problem-update.html'

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


class MonitoringPlanListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the monitoring plan of the patients in our db record."""
    template_name = 'pharmcare/monitoring-plan-list.html'
    ordering = 'id'
   # queryset = ProgressNote.objects.all().order_by(ordering)
    has_improved = models.BooleanField(default=False)

    context_object_name = 'monitoring_plan'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        organization = self.request.user.userprofile
        user = self.request.user

        try:
            if user.is_organizer or user.is_pharmacist:
                monitoring_plan_qs = MonitoringPlan.objects\
                    .filter(organization=organization)
            else:
                monitoring_plan_qs = MonitoringPlan.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                monitoring_plan_qs = monitoring_plan_qs\
                    .filter(pharmacist__user=user)

                # query the monitoring_plan_qs via filter to
                # allow the user search the content s/he wants
                monitoring_plan_qs.filter(
                    Q(frequency__icontains=query) |
                    Q(parameter_used__icontains=query)

                )\
                    .order_by('id')

            # Pagination - of Medication History Page

            search = Paginator(monitoring_plan_qs, 10)
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

    template_name = 'pharmcare/monitoring-plan-create.html'
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

    template_name = 'pharmcare/monitoring-plan-detail.html'

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
    template_name = 'pharmcare/monitoring-plan-update.html'
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

    template_name = 'pharmcare/monitoring-plan-delete.html'

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


class FollowUpPlanListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request 
    cycle to display the follow up plan of the patients in our db record."""

    template_name = 'pharmcare/follow-up-plan-list.html'
    ordering = 'id'

    context_object_name = 'follow_up_plans'

    def get(self, *args, **kwargs):

        query = self.request.GET.get('q', '')

        organization = self.request.user.userprofile
        user = self.request.user

        if query is None:
            messages.info(self.request,
                          files('pharmcare/mails/follow-up-plan.txt'))
            return render(self.request, self.template_name)

        try:

            if user.is_organizer or user.is_pharmacist:

                self.queryset = FollowUpPlan.objects\
                    .filter(organization=organization)
            else:
                self.queryset = FollowUpPlan.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
                self.queryset.filter(
                    Q(state_of_improvement_by_score__icontains=query) |
                    Q(adhered_to_medications_given__icontains=query) |
                    Q(referral__icontains=query)
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
                'follow_up_plans': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the patient follow-up plans record you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:follow-up-plan')


class FollowUpPlanCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View responsible to display patient's create follow up plan records 
    if the admin/pharmacists wants. """

    template_name = 'pharmcare/follow-up-plan-create.html'
    form_class = FollowUpPlanForm

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = FollowUpPlan.objects.filter(
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

        return super(FollowUpPlanCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s follow up plan was created successfully.')
        return reverse('pharmcare:follow-up-plan')


class FollowUpPlanDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ View responsible to display patient's follow up plan detail
    medication records if the admin/pharmacists wants. """

    template_name = 'pharmcare/follow-up-plan-detail.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset


class FollowUpPlanUpdateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's follow up plan records if the
    admin/pharmacists wants. """

    form_class = FollowUpPlanForm
    template_name = 'pharmcare/follow-up-plan-update.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:follow-up-plan')


class FollowUpPlanDeleteView(OrganizerPharmacistLoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's follow up plan records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/follow-up-plan-delete.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = FollowUpPlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset

    def get_success_url(self) -> str:
        return reverse('pharmcare:follow-up-plan')


class ProgressNoteListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle
    to display the progress note of the patients in our db record."""

    template_name = 'pharmcare/progress-note-list.html'
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
                self.queryset.filter(
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
    template_name = 'pharmcare/progress-note-create.html'
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
    template_name = 'pharmcare/progress-note-detail.html'

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
    template_name = 'pharmcare/progress-note-update.html'

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
    template_name = 'pharmcare/progress-note-delete.html'

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


class PatientListView(OrganizerPharmacistLoginRequiredMixin, ListView):
    """ Handles request-response cycle made by the admin/pharmacists regarding 
    the patients pharmacautical care record in our db
    """

    template_name = 'pharmcare/patient-info-list.html'
   # queryset = Patient.objects.all()
    context_object_name = 'patient_info'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        user = self.request.user

        try:
            if user.is_pharmacist or user.is_organizer:

                self.queryset = Patient.objects\
                    .filter(organization=user.userprofile)
            else:
                self.queryset = Patient.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
                self.queryset.filter(
                    Q(patient_unique_code__icontains=query) |
                    Q(has_improved__icontains=query) |
                    Q(patient_full_name__icontains=query)
                )\
                    .order_by('id')
                # filter by frqeuncy, slug an parameter_used based on user's search
                self.queryset = Patient.objects.filter(

                    Q(total__icontains=query) |
                    Q(medical_charge__icontains=query)

                ).distinct()

            # Pagination - of Patient

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)

            context = {
                'patient_info': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the patient info you are searching for does not
                exist. It was deleted by {user.username.title()}""")
            return redirect('pharmcare:patient-info')


class PatientCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ Handles request-response cycle made by the admin/pharmacists to create
    a patient"""

    template_name = 'pharmcare/patient-info-create.html'
    form_class = PatientModelForm
    # queryset = Patient.objects.all()

    def get_queryset(self):

        organization = self.request.user.userprofile
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            queryset = Patient.objects.filter(
                organization=organization)
        else:
            queryset = Patient.objects.filter(
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

        # Patient.objects.create(pharmacist=user.pharmacist.organization)
        return super(PatientCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        pk = self.get_object().id
        return reverse('pharmcare:patient-info')


class PatientsDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ Handles request-response cycle made by the admin/pharmacists to 
    delete a patient record"""
    template_name = 'pharmcare/patient-info-detail.html'
    context_object_name = "patient_qs"
    # queryset = Patient.objects.all()

    def get_success_url(self):
        return reverse('pharmcare:patients-detail')

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer or user.is_pharmacist:
            queryset = Patient.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Patient.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


class PatientUpateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ Handles request-response cycle made by the admin/pharmacists to update 
    a patient record"""
    template_name = 'pharmcare/patient-info-update.html'
    # queryset = Patient.objects.all()
    form_class = PatientModelForm

    def get_success_url(self):
        return reverse('pharmcare:patient-info')

    def get_queryset(self):

        user = self.request.user

        if user.is_organizer or user.is_pharmacist:

            queryset = Patient.objects.filter(
                organization=user.userprofile)
        else:
            """ queryset = Category.objects.filter(
                organization=user.pharmacist.organization) """

            queryset = Patient.objects.filter(
                pharmacist=user.pharmacist.organization
            )
            queryset = queryset.filter(pharmacist__user=user)

        return queryset


@login_required
def delete_patient_view(request, pk, *args, **kwargs):
    """Handles request-response cycle made by the admin/pharmacists to delete
    each patient record."""
    template_name = 'pharmcare/patient-info-detail.html'

    user = request.user

    if user.is_organizer:
        patient = Patient.objects.get(
            organization=user.userprofile, pk=pk, *args, **kwargs)

    else:
        patient = Patient.objects.get(
            organization=user.pharmacist.organization, pk=pk, *args, **kwargs)

        patient = Patient.objects.get(
            pharmacist__user=user, pk=pk, *args, **kwargs)

    context = {"patient-info": patient}
    try:
        if request.method == "POST":
            return render(request, template_name, context)
        patient.delete()
        messages.success(
            request, 'The patient information was successfully deleted.')
        return redirect('pharmcare:patient-info')

    except ObjectDoesNotExist:
        messages.info(
            request, 'The patient information you are looking for \
                does not exist.')
        return render(request, "pharmcare/patient-info-list")


class PatientSummaryListView(OrganizerPharmacistLoginRequiredMixin,
                             ListView):
    """ Handles request-response cycle made by the admin/pharmacists regarding 
    the patients pharmacautical care record in our db"""

    template_name = 'pharmcare/patients-list.html'
    # queryset = Patient.objects.all()
    context_object_name = 'patient_list'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        organization = self.request.user.userprofile
        user = self.request.user

        try:
            if user.is_organizer or user.is_pharmacist:
                patient_pharmcare_summary = PharmaceuticalCarePlan.objects\
                    .filter(organization=organization)
            else:
                patient_pharmcare_summary = PharmaceuticalCarePlan.objects\
                    .filter(pharmacist=user.pharmacist.organization)

                patient_pharmcare_summary = patient_pharmcare_summary\
                    .filter(pharmacist__user=user)

                # query the patient_pharmcare_summary via filter to
                # allow the user search the content s/he wants
                patient_pharmcare_summary.filter(
                    Q(patient_unique_code__icontains=query) |
                    Q(has_improved__icontains=query) |
                    Q(patient_full_name__icontains=query)
                )\
                    .order_by('id')

            # Pagination - of Medication History Page
            for p in patient_pharmcare_summary:
                """  for p in p.patients.all():
                    print(p.get_full_name()) """
                print(p.date_created)

            search = Paginator(patient_pharmcare_summary, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)

            context = {
                'patient_list': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the patient summary record you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:patient')


class PatientSummaryCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ Handles request-response cycle made by the admin/pharmacists
    to create a patient"""

    template_name = 'pharmcare/patients-create.html'
   # queryset = PharmaceuticalCarePlan.objects.all()
    form_class = PharmaceuticalCarePlanModelForm

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
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
        return super(PatientSummaryCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        return reverse('pharmcare:patients')


class PatientSummaryDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ Handles request-response cycle made by the admin/pharmacists to 
    delete a patient record"""
    template_name = 'pharmcare/patients-detail.html'
    context_object_name = "patient_qs"
    # queryset = PharmaceuticalCarePlan.objects.all()

    def get_success_url(self):
        return reverse('pharmcare:patients-detail')

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=self.request.user)

        return self.queryset


class PatientSummaryUpateView(OrganizerPharmacistLoginRequiredMixin, UpdateView):
    """ Handles request-response cycle made by the admin/pharmacists to update 
    a patient record"""
    template_name = 'pharmcare/patients-update.html'
   # queryset = PharmaceuticalCarePlan.objects.all()
    form_class = PharmaceuticalCarePlanModelForm

    def get_queryset(self, *args, **kwargs):
        """ function that gets the specific queryset of the user for 
        pharmacist/organization to view for further records. """
        user = self.request.user
        if user.is_organizer or user.is_pharmacist:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = PharmaceuticalCarePlan.objects.filter(
                organization=user.pharmacist.organization)

            self.queryset = self.queryset.filter(
                pharmacist__user=user)

        return self.queryset

    def get_success_url(self):
        return reverse('pharmcare:patients')


@login_required
def delete_patient_summary(request, pk, *args, **kwargs):
    """Handles request-response cycle made by the admin/pharmacists to delete
    each patient record."""
    template_name = 'pharmcare/patients-detail.html'

    user = request.user

    if user.is_organizer or user.is_pharmacist:

        patient_pharmcare_summary = PharmaceuticalCarePlan.objects.get(
            organization=user.userprofile, id=pk, *args, **kwargs)

    else:
        patient_pharmcare_summary = PharmaceuticalCarePlan.objects.get(
            organization=user.pharmacist.organization, id=pk, *args, **kwargs)

        patient_pharmcare_summary = PharmaceuticalCarePlan.objects.get(
            pharmacist__user=user, id=pk, *args, **kwargs)

        context = {"patient": patient_pharmcare_summary}

        try:
            if request.method == "POST":
                return render(request, template_name, context)
            patient_pharmcare_summary.delete()
            return redirect('pharmcare:patients')

        except ObjectDoesNotExist:
            messages.info(
                request, 'The patient summary information you are looking for\
                    does not exist.')
            return render(request, "pharmcare/patients-list")
