from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from utils import files, slug_modifier
from django.core.exceptions import ObjectDoesNotExist
from agents.mixins import OrganizerAgentLoginRequiredMixin
from django.core.mail import send_mail
from django.db.utils import IntegrityError
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class PatientDetailListView(LoginRequiredMixin, ListView):
    """ Patient view class: display the model data as a request made by the client
    on the server when needed.

    Important information:

    Please note that agent and pharmacist are used interchangeable. However, for the 
    context, it is better we use pharmacist here.
    """

    ordering = 'first_name'
    context_object_name = 'patients'
    template_name = 'pharmcare/pharmcare-list.html'

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
            self.queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=True)

        else:
            self.queryset = PatientDetail.objects.filter(
                organization=user.pharmacist.organization, pharmacist__isnull=True)

            self.queryset = self.queryset.filter(
                pharamacist__user=self.request.user)

        self.queryset = self.queryset.order_by(self.ordering).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(gender__icontains=query)

        ).distinct()
        print(query)

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
        if not self.request.user.is_organizer or not \
                self.request.user.is_agent:
            messages.error(self.request, f'Apologies {
                           self.request.user}, you don\'t have access to this link because you are not a registered pharmacist. Kindly contact the admin.')
            return reverse('landing-page')

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split patients that have not been 
        assigned yet to an agent """

        context = super(PatientDetailListView, self).get_context_data()
        user = self.request.user

        if user.is_organizer or user.is_agent:

            # agent__isnull= True -> to check whether a foreign key is null.
            self.queryset = PatientDetail.objects.filter(
                organization=user.userprofile, pharmacist__isnull=True
            )

            context.update({
                "unassigned_patients": self.queryset,

            })

            # context['patients'] = queryset

        return context


class PatientDetailCreateView(LoginRequiredMixin, CreateView):
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
        return super(PatientDetailCreateView, self).form_valid(form)


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
        form = form.save(commit=False)
        form.date_created = timezone.now()
        form.save()
        messages.info(self.request,
                      f'{patient_first_name} {patient_last_name} data was successfully updated! ')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pharmcare:patient')


class DeletePatientDetailView(LoginRequiredMixin, DeleteView):
    """ Handles all the delete entry request made by the registered user """
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

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class MedicationHistoryCreateView(LoginRequiredMixin, CreateView):
    """ View responsible to display patient's create medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-create.html'
    form_class = MedicationHistoryForm
    queryset = MedicationHistory.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:medication-history')

    def form_valid(self, form):
        form = form.save(commit=False)
        form.date_created = timezone.now()
        form.save()
        return super(MedicationHistoryCreateView, self).form_valid(form)


class MedicationHistoryDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-detail.html'
    queryset = MedicationHistory.objects.all()
    context_object_name = 'med_history'


class MedicationHistoryUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's medication records if the
    admin/pharmacists wants. """
    form_class = MedicationHistoryForm
    template_name = 'pharmcare/medication-history-update.html'
    queryset = MedicationHistory.objects.all()
    context_object_name = 'med_history'

    def get_success_url(self) -> str:
        return reverse('pharmcare:medication-history')


class MedicationHistoryDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's medication records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-delete.html'
    queryset = MedicationHistory.objects.all()
    context_object_name = 'med_history'

    def get_success_url(self) -> str:
        return reverse('pharmcare:medication-history')


class MedicationChangesListView(OrganizerAgentLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle to display
    the medication changes of the patients in our db record."""
    template_name = 'pharmcare/medication-changes-list.html'
    ordering = 'id'
    queryset = MedicationChanges.objects.all().order_by(ordering)

    context_object_name = 'med_changes'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')
            if query is None:
                messages.info(self.request,
                              files('/pharmcare/mails/medchanges.txt'))
                return render(self.request, self.template_name)

            # filter by dose an route based on user's search
            self.queryset = MedicationChanges.objects.filter(

                Q(dose__icontains=query) |
                Q(route__icontains=query)

            ).distinct()

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class MedicationChangesCreateView(LoginRequiredMixin, CreateView):
    """ View responsible to display patient's create medication changes records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-changes-create.html'
    form_class = MedicationChangesForm
    queryset = MedicationChanges.objects.all()

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Medication changes was created successfully.')
        return reverse('pharmcare:medication-changes')

    def form_valid(self, form):
        """ instantously create and save patient's slug and start_or_continued
        date to our db prior to saving every entry provided that form is valid."""
        form = form.save(commit=False)
        form.slug = slug_modifier()
        form.date_created = timezone.now()
        form.start_or_continued_date = timezone.now().date()
        form.save()
        return super(MedicationChangesCreateView, self).form_valid(form)


class MedicationChangesDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's changes detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-changes-detail.html'
    queryset = MedicationChanges.objects.all()


class MedicationChangesUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's medication changes records if the
    admin/pharmacists wants. """
    form_class = MedicationChangesForm
    template_name = 'pharmcare/medication-changes-update.html'
    queryset = MedicationChanges.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:medication-changes')

    """ def get_success_url(self) -> str:
        # call self.get_object() to return the actual lead
        pk = self.get_object().id
        return reverse('pharmcare:medication-changes', kwargs={"pk": pk}) """


class MedicationChangesDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's medication changes records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/medication-history-delete.html'
    queryset = MedicationChanges.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:medication-changes')


class AnalysisOfClinicalProblemListView(OrganizerAgentLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle to display
    the analysis of clinical problem of the patients in our db record."""
    template_name = 'pharmcare/analysis-of-clinical-problem-list.html'
    ordering = 'id'
    queryset = AnalysisOfClinicalProblem.objects.all().order_by(ordering)

    context_object_name = 'analysis_of_cp'  # cp -> clinical problem

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')
            if query is None:
                messages.info(self.request,
                              files('/pharmcare/mails/analysisofcp.txt'))
                return render(self.request, self.template_name)

            # filter by dose an route based on user's search
            self.queryset = AnalysisOfClinicalProblem.objects.filter(

                Q(clinical_problem__icontains=query) |
                Q(priority__icontains=query) |
                Q(slug__icontains=query)

            ).distinct()

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class AnalysisOfClinicalProblemCreateView(OrganizerAgentLoginRequiredMixin, CreateView):
    """ View responsible to display patient's create 'analysis of clinical problem'  records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/analysis-of-clinical-problem-create.html'
    form_class = AnalysisOfClinicalProblemForm
    queryset = AnalysisOfClinicalProblem.objects.all()

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Medication changes was created successfully.')
        return reverse('pharmcare:analysis-of-cp')

    def form_valid(self, form):
        form = form.save(commit=False)
        form.slug = slug_modifier()
        form.save()
        return super(AnalysisOfClinicalProblemCreateView, self).form_valid(form)


class AnalysisOfClinicalProblemDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's changes detai analysis of clinical problem records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/analysis-of-clinical-problem-detail.html'
    queryset = AnalysisOfClinicalProblem.objects.all()


class AnalysisOfClinicalProblemUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's analysis of clinical problem  records if the
    admin/pharmacists wants. """
    form_class = AnalysisOfClinicalProblemForm
    template_name = 'pharmcare/analysis-of-clinical-problem-update.html'
    queryset = AnalysisOfClinicalProblem.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:analysis-of-cp')


class AnalysisOfClinicalProblemDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient' analysis of clinical problem  records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/analysis-of-clinical-problem-update.html'
    queryset = AnalysisOfClinicalProblem.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:analysis-of-cp')


class MonitoringPlanListView(OrganizerAgentLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle to display
    the monitoring plan of the patients in our db record."""
    template_name = 'pharmcare/monitoring-plan-list.html'
    ordering = 'id'
    queryset = MonitoringPlan.objects.all().order_by(ordering)
    has_improved = models.BooleanField(default=False)

    context_object_name = 'monitoring_plan'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')
            if query is None:
                messages.info(self.request,
                              files('/pharmcare/mails/monitoring-plan.txt'))
                return render(self.request, self.template_name)

            # filter by frqeuncy, slug an parameter_used based on user's search
            self.queryset = MonitoringPlan.objects.filter(

                Q(parameter_used__icontains=query) |
                Q(frequency__icontains=query)

            ).distinct()

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class MonitoringPlanCreateView(LoginRequiredMixin, CreateView):
    """ View responsible to display patient's create  monitoring plan records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/monitoring-plan-create.html'
    form_class = MonitoringPlanForm
    queryset = MonitoringPlan.objects.all()

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s monitoring plan was created successfully.')
        return reverse('pharmcare:monitoring-plan')

    def form_valid(self, form):
        form = form.save(commit=False)
        form.slug = slug_modifier()
        form.save()
        return super(MonitoringPlanCreateView, self).form_valid(form)


class MonitoringPlanDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's  monitoring plan detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/monitoring-plan-detail.html'
    queryset = MonitoringPlan.objects.all()


class MonitoringPlanUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's  monitoring plan records if the
    admin/pharmacists wants. """
    form_class = MonitoringPlanForm
    template_name = 'pharmcare/monitoring-plan-update.html'
    queryset = MonitoringPlan.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:monitoring-plan')


class MonitoringPlanDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's  monitoring plan records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/monitoring-plan-delete.html'
    queryset = MonitoringPlan.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:monitoring-plan')


class FollowUpPlanListView(OrganizerAgentLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle to display
    the follow up plan of the patients in our db record."""
    template_name = 'pharmcare/follow-up-plan-list.html'
    ordering = 'id'
    queryset = FollowUpPlan.objects.all().order_by(ordering)

    context_object_name = 'follow_up_plans'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')

            if query is None:
                messages.info(self.request,
                              files('pharmcare/mails/follow-up-plan.txt'))
                return render(self.request, self.template_name)

            # filter by frqeuncy, slug an parameter_used based on user's search
            self.queryset = FollowUpPlan.objects.filter(

                Q(state_of_improvement_by_score__icontains=query) |
                Q(adhered_to_medications_given__icontains=query) |
                Q(referral__icontains=query)

            )

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class FollowUpPlanCreateView(LoginRequiredMixin, CreateView):
    """ View responsible to display patient's create follow up plan records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/follow-up-plan-create.html'
    form_class = FollowUpPlanForm
    queryset = FollowUpPlan.objects.all()

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s follow up plan was created successfully.')
        return reverse('pharmcare:follow-up-plan')

    def form_valid(self, form):
        form = form.save(commit=False)
        form.slug = slug_modifier()
        form.save()
        return super(FollowUpPlanCreateView, self).form_valid(form)


class FollowUpPlanDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's follow up plan detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/follow-up-plan-detail.html'
    queryset = FollowUpPlan.objects.all()


class FollowUpPlanUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's follow up plan records if the
    admin/pharmacists wants. """
    form_class = FollowUpPlanForm
    template_name = 'pharmcare/follow-up-plan-update.html'
    queryset = FollowUpPlan.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:follow-up-plan')


class FollowUpPlanDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's follow up plan records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/follow-up-plan-delete.html'
    queryset = FollowUpPlan.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:follow-up-plan')


class ProgressNoteListView(OrganizerAgentLoginRequiredMixin, ListView):
    """ A class view that handles registered/allowed user's request cycle to display
    the progress note of the patients in our db record."""
    template_name = 'pharmcare/progress-note-list.html'
    ordering = 'id'
    queryset = ProgressNote.objects.all().order_by(ordering)

    context_object_name = 'progress_notes'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if user.is_pharmacist and user.is_agent:
            query = self.request.GET.get('q', '')

            if query is None:
                messages.info(self.request,
                              files('pharmcare/mails/progress-note.txt'))
                return render(self.request, self.template_name)

            # filter by frqeuncy, slug an parameter_used based on user's search
            self.queryset = ProgressNote.objects.filter(

                Q(notes__icontains=query) |
                Q(slug__icontains=query)

            ).distinct()

            # Pagination - of Medication History Page

            search = Paginator(self.queryset, 10)
            page = self.request.GET.get('page')

            try:
                self.queryset = search.get_page(page)

            except PageNotAnInteger:
                self.queryset = search.get_page(1)

            except EmptyPage:
                self.queryset = search.get_page(search.num_pages)
        return self.queryset


class ProgressNoteCreateView(LoginRequiredMixin, CreateView):
    """ View responsible to display patient's create progress note records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/progress-note-create.html'
    form_class = ProgressNoteForm
    queryset = ProgressNote.objects.all()

    def get_success_url(self) -> str:
        messages.info(
            self.request, 'Patient\'s progress note was created successfully.')
        return reverse('pharmcare:progress-notes')

    def form_valid(self, form):
        """ dynamically create and save patient's slug identifier in our db. """
        progress_note = form.save(commit=False)
        progress_note.slug = slug_modifier()
        progress_note.date_created = timezone.now()
        progress_note.save()
        return super(ProgressNoteCreateView, self).form_valid(form)


class ProgressNoteDetailView(LoginRequiredMixin, DetailView):
    """ View responsible to display patient's progress note detail medication records 
    if the admin/pharmacists wants. """
    template_name = 'pharmcare/progress-note-detail.html'
    queryset = ProgressNote.objects.all()


class ProgressNoteUpdateView(LoginRequiredMixin, UpdateView):
    """ View responsible for updating patient's progress note records if the
    admin/pharmacists wants. """
    form_class = ProgressNoteForm
    template_name = 'pharmcare/progress-note-update.html'
    queryset = ProgressNote.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:progress-notes')


class ProgressNoteDeleteView(LoginRequiredMixin, DeleteView):
    """ View responsible to delete patient's progress note records if
    the admin/pharmacists wants. """
    template_name = 'pharmcare/progress-note-delete.html'
    queryset = ProgressNote.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:progress-notes')


class PatientSummaryListView(OrganizerAgentLoginRequiredMixin, DetailView):
    """ Handles request-response cycle made by the admin/pharmacists regarding 
    the patients pharmacautical care record in our db"""

    template_name = 'pharmcare/patient-list.html'
    # queryset = Patient.objects.all()
    context_object_name = 'patient_list'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')

        patient_pharmcare_summary = PharmaceuticalCarePlan.objects.get(
            user=self.request.user
        )

        """  # paginate  patients list 
        paginate_pt = Paginator(patient_pharmcare_summary, 1)
        page = self.request.GET.get('page')
        
        try:
            patient_list_qs = paginate_pt.get_page(page)
        
        except PageNotAnInteger:
            patient_list_qs = paginate_pt.get_page(1)
        except EmptyPage:
            patient_list_qs = paginate_pt.get_page(paginate_pt.num_pages)
        """
        context = {
            'patient_list': patient_pharmcare_summary
        }
       # print(patient_pharmcare_summary.id)
        return render(self.request, self.template_name, context)


class PatientSummaryCreateView(OrganizerAgentLoginRequiredMixin, CreateView):
    """ Handles request-response cycle made by the admin/pharmacists to create a patient"""
    template_name = 'pharmcare/patient-create.html'
    models = Patient
    form_class = PatientModelForm
    print(form_class)

    def get_success_url(self) -> str:
        return reverse('patients')

    def form_valid(self, form):
        user = self.request.user

        form = form.save(commit=False)
        # fetch and save the current user
        form.pharmacist = user
        print(form.pharmacist)
        form.save()
        super().form_valid(self, form)


class PatientSummaryDetailView(OrganizerAgentLoginRequiredMixin, DetailView):
    """ Handles request-response cycle made by the admin/pharmacists to view each patient record."""
    template_name = 'pharmcare/patient-detail.html'
    queryset = PharmaceuticalCarePlan.objects.all()

    def get_success_url(self):

        return reverse("pharmcare:patient-list")

class PatientSummaryUpateView(OrganizerAgentLoginRequiredMixin, UpdateView):
    """ Handles request-response cycle made by the admin/pharmacists to update a patient record"""
    template_name = 'pharmcare/patient-list.html'
    queryset = PharmaceuticalCarePlan.objects.all()


class PatientSummaryDeleteView(OrganizerAgentLoginRequiredMixin, DeleteView):
    """ Handles request-response cycle made by the admin/pharmacists to delete a patient record"""
    template_name = 'pharmcare/patient-list.html'
    queryset = PharmaceuticalCarePlan.objects.all()
