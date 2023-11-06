
from django.db.models.query import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from .models import Song, Category, Subscribe
from .forms import SubscribedModelForm
from django.core.mail import send_mail
from django.urls import reverse
from utils import files
from django.views import generic



def navigation(request):

    return render(request, 'songs/navigation.html')


class FooterView(LoginRequiredMixin, generic.CreateView):
    template_name = 'songs/footer.html'
    form_class = SubscribedModelForm
    model = Subscribe
    
    def form_valid(self, form):
        send_mail(
                subject="Newsletter SUbscription",
                message= files('songs/mails/subscription.txt'),
                from_email='blaise@gmail.com',
                recipient_list= ['kester@gmail.com', 'Onyedika@gmail.com'],
                fail_silently=False
            )
        return super(FooterView, self).form_valid(form)

    def get_success_url(self):
         return reverse('leads:home-page')
    
    
class UnsubscribedView(generic.DeleteView):
    template_name = 'unsubscribed.html'

    def get_queryset(self):
        user = self.request.user
        # initial queryset for subscribed users
        queryset = Subscribe.objects.filter(email=user.email)

        return queryset.order_by('id')

    def get_success_url(self):
        send_mail(
                subject="Newsletter SUbscription",
                message= files('songs/mails/unsubscribed.txt'),
                from_email='blaise@gmail.com',
                recipient_list= ['kester@gmail.com', 'Onyedika@gmail.com'],
                fail_silently=False
            )
        return reverse('leads:home-page')
       
    
class CategoryListView(generic.ListView):
    model = Category
    template_name = 'songs/music_category_list.html'


class SongsByCategoryView(generic.ListView):
    ordering = 'id'
    paginate_by = 10
    # context_object_name = 'songs'
    template_name = 'songs/music_by_category.html'

    def get_queryset(self):

        # the following category will also be added to the context data
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Song.objects.filter(category=self.category)
        queryset = queryset.order_by(self.ordering)

        return queryset
       # return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context











