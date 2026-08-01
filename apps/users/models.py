from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='users/profile_pictures',
        null=True,
        blank=True,
    )
    bio = models.TextField(null=True, blank=True)
