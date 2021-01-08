from django.urls import path

from .views import *


urlpatterns = [
    #path('', index, name='index'),
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout_view/', logout_view, name='logout_view'),
]
