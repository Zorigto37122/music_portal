from django.contrib import admin
from .models import Performer, Album, Composition, UserInteraction

@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ('name',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'performer', 'release_year', 'type')
    list_filter = ('type', 'release_year')
    search_fields = ('title', 'performer__name')

@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'duration', 'style', 'play_count')
    list_filter = ('style', 'album__performer')
    search_fields = ('title', 'album__title')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'composition', 'performer', 'timestamp')
    list_filter = ('action', 'timestamp')
