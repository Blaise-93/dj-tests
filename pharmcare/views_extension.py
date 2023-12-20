from django.urls import reverse
from agents.mixins import OrgnizerAndLoginRequiredMixin
from django.views import generic
from utils import password_setter
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.paginator import (
    PageNotAnInteger, EmptyPage,
    Paginator
    )
from django.contrib import messages
from django.db.models import Q
from .models import Pharmacist, PatientDetail
from .forms import PharmacistModelForm, PharmacistAssignedForm




class PharmacistAssignedView(OrgnizerAndLoginRequiredMixin, generic.FormView):
    """ A view responsible for creating a pharmacist form and assigning the pharmcist
    to a specific patient(s) required by the organizer when created."""

    template_name = 'pharmcare/pharmacist/assigned-pharmacist.html'
    form_class =  PharmacistAssignedForm
    context_object_name = 'assigned_pharmacist'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(PharmacistAssignedView, self)\
            .get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('pharmcare:pharmacist')

    def form_valid(self, form):
        # agent cleaned data in the model
        pharmacist = form.cleaned_data['pharmacist']

        # get key from slug in the URL
        patient_detail = PatientDetail.objects.get(slug=self.kwargs['slug'])
        # assign the leads to exact pharmacist selected
        patient_detail.pharmacist = pharmacist
        patient_detail.save()
        return super(PharmacistAssignedView, self).form_valid(form)


class PharmacistListView(OrgnizerAndLoginRequiredMixin, generic.ListView):
    """ View that handles listing and rendering pharmacist request-response 
    cycle of the organizer """
    template_name = 'pharmcare/pharmacist/pharmacist-list.html'
    context_object_name = 'pharmacists'

    def get_queryset(self):
        user_userprofile = self.request.user.userprofile
        query = self.request.GET.get('q', '')

        # filter by request user organization - so that each won't see or
        # have access to every pharmacist in other organization
        # except their respective organization

        self.queryset = Pharmacist.objects.filter(organization=user_userprofile)\
            .filter(
            Q(first_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(slug__icontains=query)
        )

        # Pagination - of Pharmacist Page

        search = Paginator(self.queryset, 10)
        page = self.request.GET.get('page')

        try:
            self.queryset = search.get_page(page)

        except PageNotAnInteger:
            self.queryset = search.get_page(1)

        except EmptyPage:
            self.queryset = search.get_page(search.num_pages)

        return self.queryset


class PharmacistCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'pharmcare/pharmacist/pharmacist-create.html'
    form_class = PharmacistModelForm
    queryset = Pharmacist.objects.all()

    def get_success_url(self) -> str:
        return reverse('pharmcare:pharmacist-list')

    def form_valid(self, form):
        # call form.save()
        user = form.save(commit=False)
        # create pharmacist user
        user.is_pharmacist = True
        user.is_organizer = False
        # set password
        user.set_password(password_setter())
        user.save()

        email = form.cleaned_data.get('email')
        # create the pharmacist from the form we saved
        Pharmacist.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )

        username= form.cleaned_data['username']
   
        context = {
            'user': username,
        }

        # send email to the user

        send_mail(
            subject='Pharmaceutical Care Mangement Invitation',
            message=\
                render_to_string\
                    ('pharmcare/pharmacist/pharmacist-invite.html', context),
            from_email="tests@blaise.com",
            recipient_list=[email, ]
        )
        
        messages.success(self.request, f"""The pharmacist request form was
            created successfully! Kindly follow up {username.title()} 
            to make sure that other registrations are carried out successfully.""")
        
        return super(PharmacistCreateView, self).form_valid(form)
    
    """  def get_success_url(self):
        messages.success(self.request, f"Kindly follow up {self.username} ")
        return reverse('pharmcare:pharmacist-list') """
    

class PharmacistDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):

    context_object_name = 'pharmacist'
    template_name = 'pharmcare/pharmacist/pharmacist-detail.html'

    def get_queryset(self):
        userprofile = self.request.user.userprofile
        return Pharmacist.objects.filter(organization=userprofile)

    def get_success_url(self):

        return reverse('pharmcare:pharmacist-detail')


class PharmacistUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    """ Update the pharmacist record created by the organizer """
    template_name = "pharmcare/pharmacist/pharmacist-update.html"
    context_object_name = 'pharmacist'
    form_class = PharmacistModelForm

    def get_queryset(self):
        """ This function get the `user profile queryset`. Since we don't want 
        pharmacist to update information that belongs to other agents in another
        organization which s/he does not manage. 
            """
        userprofile = self.request.user.userprofile
        return Pharmacist.objects.filter(organization=userprofile)

    def get_success_url(self):
        messages.info(self.request, "You have successfully updated the pharmacist!")
        return reverse('pharmcare:pharmacist-list')


class PharmacistDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'pharmcare/pharmacist/pharmacist-delete.html'

    def get_queryset(self):
        userprofile = self.request.user.userprofile
        return Pharmacist.objects.filter(organization=userprofile)

    def get_success_url(self):
        messages.success(self.request, "You had successfully deleted the \
                         pharmacist assigned for the attendant register.")
        return reverse("pharmcare:pharmacist-list")
