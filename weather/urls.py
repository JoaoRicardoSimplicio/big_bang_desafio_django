from django.urls import path
from . import views

urlpatterns = [
    path('', views.Initial, name='initial'),
    path('consultar/', views.Consult, name='consult'),
    path('teste/', views.GetPlaylistSpotify, name='teste')
]