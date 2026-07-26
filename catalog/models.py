"""
Video game catalog models module.

Contains abstract and concrete Django ORM models for managing
information about games, genres, characters, and quests.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .utils import current_year, generate_unique_slug

TITLE_MAX_LENGTH = 120
NAME_MAX_LENGTH = 200
FIRST_VIDEOGAME_RELEASE_YEAR = 1958


class SlugModel(models.Model):
    """
    Abstract base model for generating unique URLs (slugs).

    Automatically generates a unique `slug` before saving the object,
    using the field specified in `slug_source_field` as the source.

    Attributes:
        slug (SlugField): A unique string identifier for the URL.
        slug_source_field (str): The name of the model field used to generate the slug.
    """
    slug = models.SlugField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        blank=True
    )
    slug_source_field = 'title'

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(
                self,
                slugable_field_name=self.slug_source_field
            )
        super().save(*args, **kwargs)


class Genre(models.Model):
    """
    Video game genre model (e.g., RPG, Action, Strategy).

    Attributes:
        name (CharField): The unique name of the genre.
    """
    name = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(SlugModel):
    """
    Video game model.

    Stores general information about the game: title, description, release year,
    publisher, visual assets, metacritic scores, and related genres.

    Attributes:
        title (CharField): The title of the game.
        description (TextField): A detailed description of the plot and gameplay.
        release_year (IntegerField): The release year of the game (from 1958 to current year).
        publisher (CharField): The publisher of the game.
        cover_image (ImageField): The game's cover art.
        banner_image (ImageField): A banner image for the game page (optional).
        metacritic_score (FloatField): The Metacritic score (from 0 to 100).
        genres (ManyToManyField): The genres associated with the game.
        added_by (ForeignKey, nullable): The user who added the game.
            Uses on_delete=SET_NULL — unlike the other foreign keys in the model
            (PROTECT), because deleting a user account should not require deleting
            the game itself or block the user's deletion. Upon deletion, the 
            attribution is simply set to null.
        slug (SlugField): A unique slug for building the game page URL.
    """
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    description = models.TextField()
    release_year = models.IntegerField(
        validators=(
            MinValueValidator(FIRST_VIDEOGAME_RELEASE_YEAR),
            MaxValueValidator(current_year),
        )
    )
    publisher = models.CharField(max_length=NAME_MAX_LENGTH)
    cover_image = models.ImageField(upload_to='catalog/games/covers')
    banner_image = models.ImageField(
        upload_to='catalog/games/banners',
        blank=True)
    metacritic_score = models.FloatField(
        validators=(MinValueValidator(0), MaxValueValidator(100)),
    )
    genres = models.ManyToManyField(Genre, related_name='games')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_games',
    )
    slug = models.SlugField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        blank=True
    )

    def get_absolute_url(self):
        return reverse('catalog:game_detail', args=(self.slug,))

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f'{self.title} {self.release_year}'


class Character(SlugModel):
    """
    Video game character model.

    Attributes:
        name (CharField): The character's name.
        description (TextField): A biography or description of the character.
        game (ForeignKey): The game the character belongs to (PROTECT).
        photo (ImageField): An image or portrait of the character.
        slug (SlugField): A unique slug for building the character page URL.
    """
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    game = models.ForeignKey(
        'Game',
        on_delete=models.PROTECT,
        related_name='characters',
    )
    slug_source_field = 'name'
    photo = models.ImageField(upload_to='catalog/characters/photos/')
    slug = models.SlugField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        blank=True
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_characters',
    )

    def get_absolute_url(self):
        return reverse('catalog:character_detail', args=(self.slug,))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Quest(models.Model):
    """
    In-game quest or mission model.

    Attributes:
        title (CharField): The title of the quest.
        description (TextField): The description and objectives of the quest.
        game (ForeignKey): The game the quest belongs to (PROTECT).
    """
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    description = models.TextField()
    game = models.ForeignKey(
        'Game',
        on_delete=models.PROTECT,
        related_name='quests',
    )

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title
