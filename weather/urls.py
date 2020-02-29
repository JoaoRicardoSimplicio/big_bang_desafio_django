from django.urls import path
from . import views

urlpatterns = [
    path('', views.Initial, name='initial'),
    path('consultar/', views.Consultar, name='consultar'),
    path('teste/', views.GetPlaylistSpotify, name='teste')
]