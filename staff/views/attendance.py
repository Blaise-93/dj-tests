from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils import time_in_hr_min
from django.core.exceptions import ObjectDoesNotExist

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from agents.mixins import (
    OrganizerManagementLoginRequiredMixin,
    OrgnizerAndLoginRequiredMixin
)

from staff.models import Attendance, Management
from django.db.models import Q
from django.contrib import messages
from staff.forms import AttendanceModelForm


class AttendanceListView(OrganizerManagementLoginRequiredMixin, generic.ListView):
    """ Attendance list view class: displays the model data as a request made by the client
    on the server when needed. Any request made must pass certain conditions by the 
    organization responsible for the management and assigning the attendance to individual
    management (branch). 

    NB: `OrganizerManagementLoginRequiredMixin` is a customized mixins to restrict logged in 
    user to be only the management, and or organizer. It inherits `AccessMixin` class from base 
    mixins for it's functionality.
    """

    template_name = 'staff/attendance-list.html'
    context_object_name = 'attendance'
    ordering = 'id'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('q', '')
        organization = self.request.user.userprofile
        user = self.request.user

        try:
            if user.is_organizer or user.is_management:
                self.queryset = Attendance.objects\
                    .filter(organization=organization)
            else:
                self.queryset = Attendance.objects\
                    .filter(management=user.management.organization)

                self.queryset = self.queryset\
                    .filter(management__user=user)

                # query the self.queryset via filter to
                # allow the user search the content s/he wants
            self.queryset = self.queryset.filter(

                Q(full_name__icontains=query) |
                Q(staff_attendance_ref__icontains=query)

            )\
                .order_by(self.ordering)

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
                'attendance': self.queryset
            }

            return render(self.request, self.template_name, context)

        except ObjectDoesNotExist:
            messages.info(self.request,
                          f"""Apologies, the staff attendance record you are \
                              searching for does not exist.
                It was deleted by {self.request.user.username.title()}""")
            return redirect('pharmcare:attendance')

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split attendance that \
            have not been assigned yet to a manager """

        context = super(AttendanceListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:

            # if management__isnull== True
            # then update unassigned attendance
            queryset = Attendance.objects.filter(
                organization=user.userprofile, management__isnull=True
            )

            context.update({
                "unassigned_management": queryset
            })

        return context


class AttendanceCreateView(OrganizerManagementLoginRequiredMixin,
                           generic.CreateView):
    """ A view responsible for creation of attendance, (validate the form)
    when needed by the assigned management (branch) and or organizer. """
    template_name = 'staff/attendance-create.html'
    form_class = AttendanceModelForm

    def get_queryset(self):
        queryset = Attendance.objects.all()
        organization = self.request.user.userprofile

        queryset = Attendance.objects.filter(
            organization=organization)

        return queryset

    def get_success_url(self):
        return reverse('staff:attendance')

    def form_valid(self, form):
        user = self.request.user
        full_name = form.cleaned_data['full_name']

        attendance = form.save(commit=False)
        attendance.user = user
        attendance.organization = user.userprofile
        attendance.save()

        messages.info(self.request,
                      f"{full_name.title()} today's attendance was created successfully!")
        return super(AttendanceCreateView, self).form_valid(form)


class AttendanceDetailView(OrganizerManagementLoginRequiredMixin,
                           generic.DetailView):
    """ A view that handles each user attendance detail in our db for further information 
    about the record.
    """

    # queryset = Attendance.objects.all()
    template_name = "staff/attendance-detail.html"

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer or user.is_management:
            queryset = Attendance.objects.filter(organization=user.userprofile)
        else:
            queryset = Attendance.objects.filter(
                organization=user.management.organization)

            queryset = queryset.filter(management__user=user)
            # when returned django then evaluate what you filtered
        return queryset


class AttendanceUpdateView(OrganizerManagementLoginRequiredMixin, generic.UpdateView):
    """ A view responsible for updating of a specific slug of a attendance if needed 
    by the organizer or the mgmt.

    NB: Mgmt -> Management
    """

    template_name = "staff/attendance-update.html"
    context_object_name = 'attendance'
    form_class = AttendanceModelForm
    # queryset = Attendance.objects.all()

    def form_valid(self, form: BaseModelForm):
        """ create expected time of sign out in case the staff """
        full_name = form.cleaned_data['full_name']
        attendance = form.save(commit=False)

        attendance.date_sign_out_time = time_in_hr_min()
        attendance.save()

        messages.info(
            self.request, f"You have successfully updated {full_name.title()}\
                attendance record!")
        return super(AttendanceUpdateView, self).form_valid(form)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer or user.is_management:
            self.queryset = Attendance.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = Attendance.objects.filter(
                organization=user.management.organization)

            self.queryset = self.queryset.filter(
                management__user=self.request.user)

        return self.queryset

    def get_success_url(self):

        return reverse('staff:attendance')


class AttendanceDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    """ A view responsible for deletion of a specific slug if a attendance of needed 
    by the organizer or the mgmt.

    NB: Mgmt -> Management
    """
    template_name = 'staff/attendance-delete.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_organizer or user.is_management:
            self.queryset = Attendance.objects.filter(
                organization=user.userprofile)

        else:
            self.queryset = Attendance.objects.filter(
                organization=user.management.organization)

            self.queryset = self.queryset.filter(
                management__user=self.request.user)

        return self.queryset

    def get_success_url(self):
        messages.info(
            self.request, "You have successfully deleted the staff \
                attendance record!")
        return reverse('staff:attendance')
