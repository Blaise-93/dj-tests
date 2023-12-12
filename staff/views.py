from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils import password_setter
from agents.mixins import  OrganizerManagementLoginRequiredMixin, OrgnizerAndLoginRequiredMixin
from .models import Management, Attendance
from .forms import ManagementModelForm, AttendanceModelForm
class StaffListView(OrganizerManagementLoginRequiredMixin, generic.ListView):
    
    template_name = 'staff/staff-list.html'
    context_object_name = 'attendance'
    
    


class ManagementListView(OrgnizerAndLoginRequiredMixin, generic.ListView):
    template_name = 'managements/management-list.html'
    context_object_name = 'managements'

    def get_queryset(self):
        user_userprofile = self.request.user.userprofile
       

        # filter by request user organization - so that each won't see or
        # have access to every management in other organization
        # except their respective organization
        return Management.objects.filter(organization=user_userprofile)


class ManagementCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'staff/management-create.html'
    form_class = ManagementModelForm
    queryset = Management.objects.all()

    def get_success_url(self) -> str:
        return reverse('staff:management-list')

    def form_valid(self, form):
        # call form.save()
        user = form.save(commit=False)
        # create agent user
        user.is_management = True
        user.is_organizer = False
        # set password
        user.set_password(password_setter())
        user.save()

        email = form.cleaned_data.get('email')
        # create the agent from the form we saved
        Management.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        context = {
                    'user':f'{ first_name }{ last_name }',
                    'user_temp_password': user.set_password
                    }

        # send email to the user
        
        send_mail(
            subject='Daily Attendance Registrar',
            message=render_to_string('staff/attendance-invite.html', context),
            from_email="tests@blaise.com",
            recipient_list=[email, ]
        )
        return super(ManagementCreateView, self).form_valid(form)


class ManagementDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):

    context_object_name = 'agent'
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
        return reverse('staff:management-list')


class ManagementDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'staff/management-delete.html'

    def get_queryset(self):
        userprofile = self.request.user.userprofile
        return Management.objects.filter(organization=userprofile)

    def get_success_url(self):
        return reverse("staff:management-list")




