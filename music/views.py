from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import JsonResponse, HttpResponse
from .models import Performer, Album, Composition, UserInteraction
from .forms import RussianUserCreationForm, RussianAuthenticationForm

class HomeView(ListView):
    template_name = 'music/home.html'
    context_object_name = 'featured_albums'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Album.objects.filter(
                Q(title__icontains=query) | Q(performer__name__icontains=query)
            ).order_by('-release_year')
        return Album.objects.all().order_by('-release_year')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query:
            context['top_performers'] = Performer.objects.filter(name__icontains=query)
            context['search_compositions'] = Composition.objects.filter(
                Q(title__icontains=query) | Q(album__title__icontains=query) | Q(album__performer__name__icontains=query)
            ).order_by('-play_count')[:10]
            context['is_search'] = True
        else:
            context['top_performers'] = Performer.objects.annotate(
                likes=Count('userinteraction', filter=Q(userinteraction__action='FAVORITE_PERFORMER'))
            ).order_by('-likes')[:5]
            context['search_compositions'] = []
            context['is_search'] = False
        return context

class PerformerDetailView(DetailView):
    model = Performer
    template_name = 'music/performer_detail.html'
    context_object_name = 'performer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = self.object.albums.all().order_by('-release_year')
        context['top_tracks'] = Composition.objects.filter(album__performer=self.object).order_by('-play_count')[:5]
        return context

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'music/album_detail.html'
    context_object_name = 'album'

class CompositionPlayView(View):
    def post(self, request, pk):
        composition = get_object_or_404(Composition, pk=pk)
        composition.play_count += 1
        composition.save()
        
        if request.user.is_authenticated:
            UserInteraction.objects.create(
                user=request.user,
                composition=composition,
                action='LISTEN'
            )
        
        return JsonResponse({'status': 'playing', 'play_count': composition.play_count})

class InteractionView(LoginRequiredMixin, View):
    def post(self, request, type, pk):
        action_map = {
            'like_composition': ('LIKE', Composition),
            'favorite_performer': ('FAVORITE_PERFORMER', Performer),
        }
        
        if type not in action_map:
            return JsonResponse({'error': 'Неверное действие'}, status=400)
            
        action, model = action_map[type]
        obj = get_object_or_404(model, pk=pk)
        
        interaction, created = UserInteraction.objects.get_or_create(
            user=request.user,
            action=action,
            **{'composition' if model == Composition else 'performer': obj}
        )
        
        if not created:
            interaction.delete()
            status = 'removed'
        else:
            status = 'added'
            
        return JsonResponse({'status': status})

class DownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        composition = get_object_or_404(Composition, pk=pk)
        composition.download_count += 1
        composition.save()
        
        UserInteraction.objects.create(
            user=request.user,
            composition=composition,
            action='DOWNLOAD'
        )
        
        response = HttpResponse(composition.audio_file, content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{composition.title}.mp3"'
        return response

class RegisterView(CreateView):
    form_class = RussianUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('music:login')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        favorite_performers = Performer.objects.filter(
            userinteraction__user=user,
            userinteraction__action='FAVORITE_PERFORMER'
        ).distinct()
        
        liked_compositions = Composition.objects.filter(
            userinteraction__user=user,
            userinteraction__action='LIKE'
        ).distinct()
        
        listen_history = UserInteraction.objects.filter(
            user=user,
            action='LISTEN'
        ).order_by('-timestamp')[:20]
        
        download_history = UserInteraction.objects.filter(
            user=user,
            action='DOWNLOAD'
        ).order_by('-timestamp')[:20]
        
        return render(request, 'music/profile.html', {
            'user': user,
            'favorite_performers': favorite_performers,
            'liked_compositions': liked_compositions,
            'listen_history': listen_history,
            'download_history': download_history,
        })

class MyLibraryView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        
        favorite_performers = Performer.objects.filter(
            userinteraction__user=user,
            userinteraction__action='FAVORITE_PERFORMER'
        ).distinct()
        
        liked_compositions = Composition.objects.filter(
            userinteraction__user=user,
            userinteraction__action='LIKE'
        ).distinct()
        
        listened_compositions = Composition.objects.filter(
            userinteraction__user=user,
            userinteraction__action='LISTEN'
        ).distinct().order_by('-play_count')
        
        downloaded_compositions = Composition.objects.filter(
            userinteraction__user=user,
            userinteraction__action='DOWNLOAD'
        ).distinct()
        
        return render(request, 'music/my_library.html', {
            'favorite_performers': favorite_performers,
            'liked_compositions': liked_compositions,
            'listened_compositions': listened_compositions,
            'downloaded_compositions': downloaded_compositions,
        })
