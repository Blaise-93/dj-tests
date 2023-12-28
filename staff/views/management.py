from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils import password_setter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from agents.mixins import OrgnizerAndLoginRequiredMixin


from staff.models import Management, Attendance
from django.db.models import Q
from django.contrib import messages
from staff.forms import (
    ManagementModelForm,
    ManagementAssignedForm
)



class ManagementAssignedView(OrgnizerAndLoginRequiredMixin, generic.FormView):
    """ A view responsible for creating a management form and assigning the management 
    to a specific attendance keeping records required by the organizer when created."""

    template_name = 'assigned-management.html'
    form_class = ManagementAssignedForm
    context_object_name = 'assigned'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(ManagementAssignedView, self)\
            .get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('staff:attendance')

    def form_valid(self, form):
        # agent cleaned data in the model
        management = form.cleaned_data['management']

        # get key from pk in the URL
       # lw = get_object_or_404(Attendance, slug=self.kwargs)
        lead = Attendance.objects.get(slug=self.kwargs['slug'])
        # assign the leads to exact management selected fgyhjhgfds
        lead.management = management
        lead.save()
        return super(ManagementAssignedView, self).form_valid(form)


class ManagementListView(OrgnizerAndLoginRequiredMixin, generic.ListView):
    """ View that handles listing and rendering management request-response 
    cycle of the organizer """
    template_name = 'staff/management-list.html'
    context_object_name = 'managements'

    def get_queryset(self):
        user_userprofile = self.request.user.userprofile
        query = self.request.GET.get('q', '')

        # filter by request user organization - so that each won't see or
        # have access to every management in other organization
        # except their respective organization

        self.queryset = Management.objects.filter(organization=user_userprofile)\
            .filter(
            Q(first_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(slug__icontains=query)
        )

        # Pagination - of Management Page

        search = Paginator(self.queryset, 10)
        page = self.request.GET.get('page')

        try:
            self.queryset = search.get_page(page)

        except PageNotAnInteger:
            self.queryset = search.get_page(1)

        except EmptyPage:
            self.queryset = search.get_page(search.num_pages)

        return self.queryset


class ManagementCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'staff/management-create.html'
    form_class = ManagementModelForm
    queryset = Management.objects.all()

    def get_success_url(self) -> str:
        return reverse('staff:management-list')

    def form_valid(self, form):
        # call form.save()
        user = form.save(commit=False)
        # create management user
        user.is_management = True
        user.is_organizer = False
        # set password
        user.set_password(password_setter())
        user.save()

        email = form.cleaned_data.get('email')
        # create the management from the form we saved
        Management.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )

        username = form.cleaned_data['username']

        context = {
            'user': username,
        }

        # send email to the user

        send_mail(
            subject='Daily Attendance Registrar',
            message=render_to_string('staff/attendance-invite.html', context),
            from_email=settings.FROM_EMAIL,
            recipient_list=[email, ]
        )
        return super(ManagementCreateView, self).form_valid(form)


class ManagementDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):

    context_object_name = 'management'
    template_name = 'staff/management-detail.html'

    def get_queryset(self):
        userprofile = self.request.user.userprofile
        return Management.objects.filter(organization=userprofile)

    def get_success_url(self):

        return reverse('staff:management-detail')


class ManagementUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    """ Update the management record created by the organizer """
    template_name = "staff/management-update.html"
    context_object_name = 'management'
    form_class = ManagementModelForm

    def get_queryset(self):
        """ This function get the user profile queryset. Since we don't want agent to update
        information that belongs to other agents in another organization which s/he does not 
        manage. 
            """
        userprofile = self.request.user.userprofile
        return Management.objects.filter(organization=userprofile)

    def get_success_url(self):
        messages.info(
            self.request, "You have successfully updated the management!")
        return reverse('staff:management-list')


class ManagementDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'staff/management-delete.html'

    def get_queryset(self):
        userprofile = self.request.user.userprofile
        return Management.objects.filter(organization=userprofile)

    def get_success_url(self):
        messages.success(
            self.request, "You had successfully deleted the management assigned for the attendant register.")
        return reverse("staff:management-list")
