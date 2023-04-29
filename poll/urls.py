from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vote/', views.vote, name='vote'),
    path('create/<int:pk>', views.create, name='create'),
    path('verify', views.verify, name='verify'),
    path('results', views.result, name='result'),
    path('createevent', views.createEvent, name = 'createevent')
]