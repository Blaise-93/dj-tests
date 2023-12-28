from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from agents.mixins import OrganizerPharmacistLoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView)
from pharmcare.models import *
from pharmcare.forms import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
    
    


def pharmcare_total_payment_view(request, *args, **kwargs):
    """ A view that get called once submission of user input is made 
    for the patient data - thereby collating the total payment made dynamically
    and storing it in the database"""

    patient = PharmaceuticalCarePlan.objects.get(
        user=request.user, *args, **kwargs)
    patient_total_payment = int(patient.get_total())

    try:
        # assigment payment to the pharmaceutical care
        payment = PharmaceuticalCarePlan()
        payment.total_payment = patient_total_payment
        payment.save()
    except ObjectDoesNotExist:

        messages.info(
            request, f"There was an error during the form submission")
    return redirect("pharmcare:patients")


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
