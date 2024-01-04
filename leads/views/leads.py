from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.views import generic
from agents.mixins import OrganizerAgentLoginRequiredMixin
from pharmcare.models import Team
from leads.models import Lead
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from leads.forms import (LeadModelForm,
                    AgentAssignedForm,
                    CustomUserForm,
                    )

from agents.mixins import (
    OrgnizerAndLoginRequiredMixin,
    OrganizerAgentLoginRequiredMixin
)

""" CRUD + L """

# Registration


class SignUpView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserForm

    def get_success_url(self):
        return reverse('login')


class LandingPageView(generic.TemplateView):
    template_name = "leads/landing-page.html"

    def get(self, *args, **kwargs):
        team = Team.objects.all()

        context = {
            'WHATSAPP_LINK': settings.WHATSAPP_LINK,
            'teams': team
        }
        return render(self.request, self.template_name, context)


class LeadsListView(OrganizerAgentLoginRequiredMixin, generic.ListView):
    """ Leads list view class: displays the model data as a request made by the client
    on the server when needed. Any request made must pass certain conditions by the 
    organization responsible for the management and assigning the leads to individual
    agent. """

    template_name = 'leads/leads/lead-list.html'
    context_object_name = 'leads'
    ordering = 'id'

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user

        query = self.request.GET.get('q', '')

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization, agent__isnull=False)

           # filter agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)

        # query the db via filtering the individual fields the
        # user is searching for.
        queryset = queryset.filter(
            Q(first_name__icontains=query) |
            Q(age__icontains=query) |
            Q(social_media_accounts__icontains=query)

        )

        # Pagination - Paginate the Lead
        search = Paginator(queryset, 10)

        page = self.request.GET.get('page')

        try:
            self.queryset = search.get_page(page)

        except PageNotAnInteger:
            self.queryset = search.get_page(1)

        except EmptyPage:
            self.queryset = search.get_page(search.num_pages)

        return self.queryset

    def get_context_data(self, **kwargs):
        """function that helps us to filter and split leads that have not been 
        assigned yet to an agent """

        context = super(LeadsListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            # agent__isnull= True -> to check whether a foreign key is null.
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=True
            )

            context.update({
                "unassigned_leads": queryset
            })

        return context


class LeadsCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):

    template_name = 'leads/leads/lead-create.html'
    form_class = LeadModelForm

    def get_queryset(self):
        organization = self.request.user.userprofile
        queryset = Lead.objects.filter(
            organization=organization, organization__isnull=True)
        return queryset

    def get_success_url(self):
        return reverse('leads:home-page')

    def form_valid(self, form):

        # fetch and save organization id
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()

        # create the agent from the form we saved
        Lead.objects.create(
            organization=self.request.user.userprofile
        )
        # fetch user email
        email = form.cleaned_data['email']
        send_mail(
            subject=f'Thanks, a lead has been created by {self.request.user}',
            message='Go to the site to see the new lead',
            from_email='blaisemart@gmail.com',
            recipient_list=[email, ],
        )
        return super(LeadsCreateView, self).form_valid(form)


class LeadsDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):
    # queryset = Lead.objects.all()
    template_name = "leads/leads/lead-detail.html"

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)

            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset


class LeadsUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/leads/lead-update.html"
    context_object_name = 'lead'
    form_class = LeadModelForm
    # queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse('leads:home-page')

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            return Lead.objects.filter(organization=user.userprofile)


class LeadsDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/leads/lead-delete.html'

    def get_queryset(self):
        user = self.request.user
        # initial queryset for entire organization?
        queryset = Lead.objects.filter(organization=user.userprofile)

        return queryset

    def get_success_url(self):
        return reverse('leads:home-page')


class AgentAssignedView(OrgnizerAndLoginRequiredMixin, generic.FormView):
    template_name = 'agents/agent-assigned.html'
    form_class = AgentAssignedForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AgentAssignedView, self)\
            .get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads:home-page')

    def form_valid(self, form):
        # agent cleaned data in the model
        agent = form.cleaned_data['agent']

        # get key from pk in the URL
       # lw = get_object_or_404(Lead, slug=self.kwargs)
        lead = Lead.objects.get(slug=self.kwargs['slug'])
        # assign the leads to exact agent selected fgyhjhgfds
        lead.agent = agent
        lead.save()
        return super(AgentAssignedView, self).form_valid(form)

