from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Performer(models.Model):
    PERFORMER_TYPES = [
        ('SOLO', 'Solo Performer'),
        ('GROUP', 'Group'),
        ('ORCHESTRA', 'Orchestra'),
        ('ENSEMBLE', 'Ensemble'),
    ]
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='performers/', blank=True, null=True)
    type = models.CharField(max_length=20, choices=PERFORMER_TYPES, default='SOLO')

    def __str__(self):
        return self.name

class Album(models.Model):
    ALBUM_TYPES = [
        ('ALBUM', 'Studio Album'),
        ('SINGLE', 'Single'),
        ('COMPILATION', 'Compilation'),
        ('EP', 'EP'),
    ]
    title = models.CharField(max_length=255)
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE, related_name='albums')
    release_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.date.today().year)]
    )
    cover_image = models.ImageField(upload_to='albums/', blank=True, null=True)
    type = models.CharField(max_length=20, choices=ALBUM_TYPES, default='ALBUM')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.performer.name}"

class Composition(models.Model):
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='compositions')
    audio_file = models.FileField(upload_to='music/')
    duration = models.DurationField(help_text="Duration in HH:MM:SS")
    style = models.CharField(max_length=100, blank=True)
    
    # Denormalized counts for performance (optional, but good for sorting)
    play_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('LIKE', 'Like'),
        ('DOWNLOAD', 'Download'),
        ('LISTEN', 'Listen'),
        ('FAVORITE_PERFORMER', 'Favorite Performer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE, null=True, blank=True)
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['composition', 'action']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action}"
