from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from django.urls import reverse

from django.views.generic import ListView

from django.contrib.auth import logout

'''
def index(request):
    """Домашняя страница."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return redirect(reverse('dashboard'))
            else:
                # Return a 'disabled account' error message
                ...
        else:
            # Return an 'invalid login' error message.
            ...

    return render(request, 'signin.html')
'''


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
        context = {'user_name': user_name}
        return render(request, template_name, context=context)

    #print('request = ', request.user.username)
    return redirect(reverse('index'))


@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect(reverse('index'))
