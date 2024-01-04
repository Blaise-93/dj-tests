from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
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
from django.db.models import Sum, Avg, Min, Max

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

    ordering = '-id'
    context_object_name = 'patients'
    template_name = 'pharmcare/patient_details/pharmcare-list.html'

    def get(self, *args, **kwargs):
        """  Since, it is rare to see a community pharmacy or hospital not
        managed by a pharmacists according to the law of most countries in the
        world, I think it is appropriate to give pharmacists
        permissions to collect and create patient data in the database. 
        This is a 50:50 win situation by the organization because it is
        quite inconvenient for each patient data collection he/she will be
        the one that would assign the patient to a specific pharmacist in
        the organization or the branch"""

        query = self.request.GET.get('q', '')

        organization = self.request.user.userprofile
        user = self.request.user

        if query is None:
            messages.info(self.request, files(
                '/pharmcare/mails/patient-list.txt'))
            return render(self.request, self.template_name)

        try:

            if user.is_organizer or user.is_pharmacist:

                self.queryset = PatientDetail.objects\
                    .filter(organization=organization,
                            pharmacist__isnull=True)
            elif self.queryset:
                self.queryset = PatientDetail.objects\
                    .filter(pharmacist=user.pharmacist.organization,
                            pharmacist__isnull=True)

                self.queryset = self.queryset\
                    .filter(pharmacist__user=user,
                            pharmacist__isnull=True)

                # query the self.queryset via filter to
                # allow the user search the content s/he

            queryset = PatientDetail.objects.\
                aggregate(Avg('consultation'), Sum('consultation'),
                          Max('consultation'), Min('consultation'))

            # for p in queryset:
            # print(queryset['consultation__sum'])

            self.queryset = self.queryset.filter(
                Q(gender__icontains=query) |
                Q(last_name__icontains=query) |
                Q(age__icontains=query) |
                Q(first_name__icontains=query)

            )\
                . distinct()\
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
                'patients': self.queryset,
                'total_consultation': queryset,
                "timestamp":utc_standard_time()
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.success(
                self.request, f'Patient\'s detail was created successfully. Thank you!')
            return reverse('landing-page')

    def get_success_url(self):

        return reverse('landing-page')


class PatientDetailCreateView(OrganizerPharmacistLoginRequiredMixin, CreateView):
    """ View that handles creating a patient details in our database by the 
    assigned pharmacists or the admin."""

    template_name = 'pharmcare/patient_details/pharmcare-create.html'
    form_class = PatientDetailModelForm
    context_object_name = 'patient'

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

    def get_success_url(self) -> str:
        messages.success(
            self.request, f'Patient medical details was created successfully. Thank you!')
        return reverse('pharmcare:patient')

    def form_valid(self, form):

        # fetch and save organization or pharmacist id in our db
        patient_detail = form.save(commit=False)

        patient_detail.organization = self.request.user.userprofile

        patient_detail.save()

        return super(PatientDetailCreateView, self).form_valid(form)


class PatientDetailView(OrganizerPharmacistLoginRequiredMixin, DetailView):
    """ This class shows the pharmacist/organization a detailed information of
    the patient extracted from pharmcare_patientdetail table.
    """
    template_name = "pharmcare/patient_details/pharmcare-detail.html"

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

    template_name = 'pharmcare/patient_details/pharmcare-update.html'
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
    template_name = 'pharmcare/patient_details/pharmcare-delete.html'

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
