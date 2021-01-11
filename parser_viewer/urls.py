from django.urls import path

from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout_view/', logout_view, name='logout_view'),
    path('ajax-sp-del', ajax_sp_del, name='ajax_sp_del'),
    path('ajax-sp-add', ajax_sp_add, name='ajax_sp_add'),
    path('ads/<int:sp_id>', ads, name='ads'),
]
