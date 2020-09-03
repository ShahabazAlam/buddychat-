from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class HomepageView(LoginRequiredMixin,TemplateView):
    login_url = '/user_accounts/login/'
    template_name = 'buddyapp/homepage.html'