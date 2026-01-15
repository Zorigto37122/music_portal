from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Performer, Album, Composition, UserInteraction
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import timedelta

class MusicPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.performer = Performer.objects.create(name='Test Performer', type='SOLO')
        self.album = Album.objects.create(title='Test Album', performer=self.performer, release_year=2023)
        self.composition = Composition.objects.create(
            title='Test Song',
            album=self.album,
            duration=timedelta(minutes=3),
            audio_file=SimpleUploadedFile("test.mp3", b"file_content", content_type="audio/mpeg")
        )

    def test_home_view(self):
        response = self.client.get(reverse('music:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Album')
        self.assertContains(response, 'Test Performer')

    def test_performer_detail(self):
        response = self.client.get(reverse('music:performer_detail', args=[self.performer.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Performer')

    def test_album_detail(self):
        response = self.client.get(reverse('music:album_detail', args=[self.album.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Song')

    def test_interaction_login_required(self):
        response = self.client.post(reverse('music:interaction', args=['like_composition', self.composition.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_interaction_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('music:interaction', args=['like_composition', self.composition.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserInteraction.objects.filter(user=self.user, action='LIKE', composition=self.composition).exists())

    def test_play_count(self):
        response = self.client.post(reverse('music:play_composition', args=[self.composition.pk]))
        self.assertEqual(response.status_code, 200)
        self.composition.refresh_from_db()
        self.assertEqual(self.composition.play_count, 1)
