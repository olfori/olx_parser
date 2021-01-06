from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    """Домашняя страница."""
    return render(request, 'signin.html')


@login_required(login_url='/')
def dashboard(request):
    """Dashboard page"""
    return render(request, 'dashboard.html')
