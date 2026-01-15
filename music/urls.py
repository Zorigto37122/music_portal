from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import RussianAuthenticationForm

app_name = 'music'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('performer/<int:pk>/', views.PerformerDetailView.as_view(), name='performer_detail'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('play/<int:pk>/', views.CompositionPlayView.as_view(), name='play_composition'),
    path('interact/<str:type>/<int:pk>/', views.InteractionView.as_view(), name='interaction'),
    path('download/<int:pk>/', views.DownloadView.as_view(), name='download_composition'),
    path('login/', auth_views.LoginView.as_view(authentication_form=RussianAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('my-library/', views.MyLibraryView.as_view(), name='my_library'),
]
