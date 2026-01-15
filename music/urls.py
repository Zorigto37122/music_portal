from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('performer/<int:pk>/', views.PerformerDetailView.as_view(), name='performer_detail'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('play/<int:pk>/', views.CompositionPlayView.as_view(), name='play_composition'),
    path('interact/<str:type>/<int:pk>/', views.InteractionView.as_view(), name='interaction'),
    path('download/<int:pk>/', views.DownloadView.as_view(), name='download_composition'),
]
