from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from .models import Performer, Album, Composition, UserInteraction

class HomeView(ListView):
    template_name = 'music/home.html'
    context_object_name = 'featured_albums'
    
    def get_queryset(self):
        return Album.objects.all().order_by('-release_year')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_performers'] = Performer.objects.annotate(
            likes=Count('userinteraction', filter=Q(userinteraction__action='FAVORITE_PERFORMER'))
        ).order_by('-likes')[:5]
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
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
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
