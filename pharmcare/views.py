from django.shortcuts import render
from django.views.generic import (
    CreateView, 
    ListView, 
    TemplateView,
    DeleteView,
    UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from pharmcare.models import *
from pharmcare.forms import *


class PatientView(LoginRequiredMixin, ListView):
    """ Patient view class: display the model data as a request made by the client
    on the server when needed."""
    queryset = Patient.objects.all()
    form = PatientDetailForm
    ordering = 'id'
    paginate_by = 12
    
    
    pass
    
