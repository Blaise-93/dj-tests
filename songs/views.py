from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Song, Category
from django.views import generic


def navigation(request):

    return render(request, 'songs/navigation.html')


def footer(request):
    return render(request, 'songs/footer.html')


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
