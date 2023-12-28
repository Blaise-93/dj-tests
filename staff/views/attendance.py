from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils import time_in_hr_min

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from agents.mixins import (
    OrganizerManagementLoginRequiredMixin,
    OrgnizerAndLoginRequiredMixin
)

from staff.models import Attendance
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

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user

        query = self.request.GET.get('q', '')

        if user.is_organizer:
            self.queryset = Attendance.objects.filter(
                organization=user.userprofile, management__isnull=False)
        else:
            self.queryset = Attendance.objects.filter(
                organization=user.management.organization, management__isnull=False)

           # filter the mgmt that is logged in
            self.queryset = self.queryset.filter(
                management__user=self.request.user)

        self.queryset.filter(
            Q(full_name__icontains=query) |
            Q(staff_attendance_ref__icontains=query)
        )

        # Pagination - of Attendance Page

        search = Paginator(self.queryset, 10)
        page = self.request.GET.get('page')

        try:
            self.queryset = search.get_page(page)

        except PageNotAnInteger:
            self.queryset = search.get_page(1)

        except EmptyPage:
            self.queryset = search.get_page(search.num_pages)

        return self.queryset

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split attendance that have not been 
        assigned yet to a manager """

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


class AttendanceCreateView(OrganizerManagementLoginRequiredMixin, generic.CreateView):
    """ A view responsible for creation of attendance, (validate the form)
    when needed by the assigned management (branch) and or organizer. """
    template_name = 'staff/attendance-create.html'
    form_class = AttendanceModelForm

    def get_queryset(self):
        queryset = Attendance.objects.all()
        organization = self.request.user.userprofile

        queryset = Attendance.objects.filter(
            organization=organization, organization__isnull=True)

        return queryset

    def get_success_url(self):
        return reverse('staff:attendance')

    def form_valid(self, form):

        # fetch and save organization id
        attendance = form.save(commit=False)

        # pharmacist_id = self.request.user.pharmacist.id
        if attendance.organization:
            attendance.organization = self.request.user.userprofile
            attendance.save()
        else:
            attendance.management = self.request.user.management.organization
            attendance.save()

        # create the mgmt from the form we saved
        full_name = form.cleaned_data['full_name']
        email = form.cleaned_data.get('email')
        context = {
            'user': full_name,
        }
        send_mail(
            subject='Invitation By the Management',
            message=render_to_string('staff/attendance-invite.html', context),
            from_email=settings.FROM_EMAIL,
            recipient_list=[email, ]
        )

        # fetch user email from already validated form
        messages.info(self.request, "Your attendance was created successfully")
        return super(AttendanceCreateView, self).form_valid(form)


class AttendanceDetailView(OrganizerManagementLoginRequiredMixin, generic.DetailView):
    """ A view that handles each user attendance detail in our db for further information 
    about the record.
    """

    # queryset = Attendance.objects.all()
    template_name = "staff/attendance-detail.html"

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            queryset = Attendance.objects.filter(organization=user.userprofile)
        else:
            queryset = Attendance.objects.filter(
                organization=user.management.organization)

            queryset = queryset.filter(management__user=self.request.user)
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

    def get_success_url(self):
        messages.info(
            self.request, "You have successfully updated the staff attendance record!")
        return reverse('staff:attendance')

    def form_valid(self, form: BaseModelForm):
        """ create expected time of sign out in case the staff """
        attendance = form.save(commit=False)
        attendance.date_sign_out_time = time_in_hr_min()

        attendance.save()
        return super(AttendanceUpdateView, self).form_valid(form)

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            return Attendance.objects.filter(organization=user.userprofile)


class AttendanceDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    """ A view responsible for deletion of a specific slug if a attendance of needed 
    by the organizer or the mgmt.

    NB: Mgmt -> Management
    """
    template_name = 'staff/attendance-delete.html'

    def get_queryset(self):
        user = self.request.user
        # initial queryset for entire organization?
        queryset = Attendance.objects.filter(organization=user.userprofile)

        return queryset

    def get_success_url(self):
        messages.info(
            self.request, "You have successfully deleted the staff attendance record!")
        return reverse('staff:attendance')
