from typing import Any
from django.db.models.query import QuerySet
from django.urls import reverse
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Category
from .forms import (LeadModelForm, 
                    CategoryModelForm,
                    LeadCategoryUpdateForm,
                    AgentAssignedForm,
                    CustomUserForm
)

from agents.mixins import OrgnizerAndLoginRequiredMixin, OrganizerAgentLoginRequiredMixin


""" CRUD + L """

# Registration


class SignUpView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserForm

    def get_success_url(self):
        return reverse('login')


class LandingPageView(generic.TemplateView):
    template_name = "leads/landing-page.html"


class LeadsListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead-list.html'
    context_object_name = 'leads'
    paginate_by = 10
    ordering = 'id'

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization, agent__isnull=False)
            # filter according n reassign the queryset
            # which doesnt make multiple queryset in the db

            # filter the agent user via deep filter call (agent__user: filters the lead based on the agent
            # field where that agent has a user == self.request.user )

           # filter agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset

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

    template_name = 'leads/lead-create.html'
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

        send_mail(
            subject='A lead has been created',
            message='Go to the site to see the new lead',
            from_email='blaise@gmail.com',
            recipient_list=['test2@gmail.com']
        )
        return super(LeadsCreateView, self).form_valid(form)


class LeadsDetailView(OrgnizerAndLoginRequiredMixin, generic.DetailView):
    # queryset = Lead.objects.all()
    template_name = "leads/lead-detail.html"

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
    template_name = "leads/lead-update.html"
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
    template_name = 'leads/lead-delete.html'

    def get_queryset(self):
        user = self.request.user
        # initial queryset for entire organization?
        queryset = Lead.objects.filter(organization=user.userprofile)

        return queryset.order_by('id')

    def get_success_url(self):
        return reverse('leads:home-page')


class AgentAssignedView(OrgnizerAndLoginRequiredMixin, generic.FormView):
    template_name = 'agents/agent-assigned.html'
    form_class = AgentAssignedForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AgentAssignedView, self).get_form_kwargs(**kwargs)
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
        lead = Lead.objects.get(id=self.kwargs['pk'])
        # assign the leads to exact agent selected
        lead.agent = agent
        lead.save()
        return super(AgentAssignedView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/category-list.html'
    paginate_by = 10
    context_object_name = 'category_list'
    ordering = 'id'

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user
        # initial queryset of leads for the organization
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile).order_by('id')

        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization).order_by('id')
          

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile
            )

        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)
          
        # leads that are not yet assigned by the oragnizer to the agents
        # to category.  Unassigned leads
        context.update({
            'unasssigned_lead_count': queryset.filter(category__isnull=True)
            .count(),
           # "contacted_count": category_id.count()
        })
    
        return context


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/category-detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user
        # initial queryset of leads for the organization
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:

        context = super(CategoryDetailView, self).get_context_data(**kwargs)

        # get_object() => used to fetch the actual category in the URL that matches the pk.
       # qs = Lead.objects.filter(category=self.get_object()) # 1
        """ OR """
        # lead_set: does reverse look up via foreign key, category which we had
        # declared in our lead model

        # 2 - we used our related names, leads for reverse lookup instead
        leads = self.get_object().leads.all()
        context.update({
            'leads': leads
        })

        return context


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/category-update.html'
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset

    def get_success_url(self) -> str:
        # call self.get_object() to return the actual lead
        pk = self.get_object().id
        return reverse('leads:lead-detail', kwargs={"pk": pk})


class CategoryCreateView(OrgnizerAndLoginRequiredMixin, generic.CreateView):

    template_name = 'leads/category-create.html'
    form_class = CategoryModelForm

    def get_queryset(self):
        organization = self.request.user.userprofile
        queryset = Lead.objects.filter(
            organization=organization, organization__isnull=True)
        return queryset

    def get_success_url(self):
        return reverse('leads:category-list')

    def form_valid(self, form):

        # fetch and save organization id
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()

        # create the agent from the form we saved
        Lead.objects.create(
            organization=self.request.user.userprofile
        )
 
        return super(CategoryCreateView, self).form_valid(form)
    
    
class CategoryUpdateView(OrgnizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/category-update.html"
    context_object_name = 'category'
    form_class = CategoryModelForm
    # queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse('leads:category-list')

    def get_queryset(self):
        user = self.request.user
        # login in user - an organizer?
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)
            # when returned django then evaluate what you filtered
        return queryset

class CategoryDeleteView(OrgnizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/category-delete.html'

    def get_success_url(self):
        return reverse('leads:category-list')

    def get_queryset(self):
        # login in user - an organizer?
        user = self.request.user
        # initial queryset of leads for the organization
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization)

        return queryset


    

