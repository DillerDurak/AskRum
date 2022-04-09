from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import datetime


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True, unique=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d/",null=True, blank=True)
    is_online = models.BooleanField(default=True)

    def get_online_info(self):
        if self.is_online:
            return _('Online')
        return _('Offline')

    @property
    def imageURL(self):
        try:
            url = self.avatar.url
        except:
            url = ''
        return url


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="room-images/%Y/%m/%d/", null=True, blank=True)
    moderator = models.ManyToManyField(User, related_name="moderator", blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['-updated', '-created']

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(null=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[:50]