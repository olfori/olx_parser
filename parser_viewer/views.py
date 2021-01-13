from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from django.urls import reverse

from django.views.generic import ListView

from django.contrib.auth import logout

from .models import SearchPhrases, Ad
from .models import SPManager as SPM

import json
from django.http import HttpResponse


class IndexView(ListView):
    def get(self, request):
        return render(request, 'signin.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return redirect(reverse('dashboard'))
        return render(request, 'signin.html')


@login_required(login_url='/')
def dashboard(request, template_name='dashboard.html'):
    """Dashboard page"""
    if request.user.is_authenticated:
        user_name = request.user.username

        return render(request, template_name, {
            'user_name': user_name,
            'sp_data': SPM().get_all(),
        })
    return redirect(reverse('index'))


@login_required(login_url='/')
def ads(request, sp_id, template_name='ads.html'):
    """Ads page"""
    ads = SPM().get_ads(sp_id)

    return render(request, template_name, {
        'ads': ads,
    })


@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


@login_required(login_url='/')
def ajax_sp_del(request):

    if request.method == 'POST':
        spm = SPM()
        del_id = int(request.POST['param'])
        spm.delete(del_id)
        dump = json.dumps(list(spm.get_all()))
        return HttpResponse(dump, content_type='application/json')

    return redirect(reverse('index'))


@login_required(login_url='/')
def ajax_sp_add(request):

    if request.method == 'POST':
        spm = SPM()
        phrase = request.POST['param']
        spm.get_or_create(phrase)
        dump = json.dumps(list(spm.get_all()))
        return HttpResponse(dump, content_type='application/json')

    return redirect(reverse('index'))
