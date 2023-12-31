from django.urls import reverse
from django.views import generic
from agents.mixins import OrganizerAgentLoginRequiredMixin
from typing import Any
from leads.models import Lead, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from leads.forms import (
    CategoryModelForm,
    LeadCategoryUpdateForm,

)

from agents.mixins import (
    OrgnizerAndLoginRequiredMixin,
    OrganizerAgentLoginRequiredMixin
)


class CategoryListView(OrganizerAgentLoginRequiredMixin, generic.ListView):
    template_name = 'leads/categories/category-list.html'
    context_object_name = 'category_list'
    ordering = 'id'

    def get_queryset(self):
        # login in user - an organizer?
        query = self.request.GET.get('q', '')
        user = self.request.user

        # initial queryset of leads for the organization
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile)

        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization)

        queryset = queryset.order_by(self.ordering).filter(
            Q(name__icontains=query)

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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
       # lead = get_object_or_404(Lead, slug=slug)
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile
            )

        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)

        # leads that are not yet assigned by the oragnizer to the agents
        # to category.  Unassigned leads
        category_id = queryset.filter(
            category__isnull=True)
        context.update({
            'unasssigned_lead_count': queryset.\
                filter(category__isnull=False).count(),
            # "contacted_count": category_id.count()
        })

        return context


class CategoryDetailView(OrganizerAgentLoginRequiredMixin, generic.DetailView):
    template_name = 'leads//categories/category-detail.html'
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


class LeadCategoryUpdateView(OrganizerAgentLoginRequiredMixin, 
                             generic.UpdateView):
    template_name = 'leads/leads/lead-category-update.html'
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

    template_name = 'leads//categories/category-create.html'
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
    template_name = "leads//categories/category-update.html"
    context_object_name = 'category'
    form_class = CategoryModelForm
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        slug = self.get_object().id
        return (reverse('leads:category-update', kwargs={"slug": slug}))

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
    template_name = 'leads/categories/category-delete.html'

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
