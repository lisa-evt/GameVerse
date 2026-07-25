from datetime import date
from django.urls import reverse

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from .utils import generate_unique_slug


TITLE_MAX_LENGTH = 120
NAME_MAX_LENGTH = 200
FIRST_VIDEOGAME_RELEASE_YEAR = 1958


def current_year():
    """Return the current year as an integer.

    Used as a dynamic upper bound for year validation in models.

    Returns:
        int: The current calendar year.
    """
    return date.today().year


class Genre(models.Model):
    """Represents a video game genre classification (e.g., RPG, Action, FPS).

    Attributes:
        name (CharField): The unique name of the genre (max length: 150).
    """

    name = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(models.Model):
    """Represents a video game entry in the database.

    Attributes:
        title (CharField): The title of the game (max length: 120).
        description (TextField): Detailed summary or details about the game.
        slug (SlugField): Unique URL identifier containing only Latin letters,
            numbers, hyphens, and underscores.
        release_year (IntegerField): The release year of the game, validated
            to be between 1958 and the current year.
        publisher (CharField): The company or entity that published the game
            (max length: 150).
        cover_image (ImageField): Image file representing the game's cover,
            stored in 'games/covers/'.
        metacritic_score (FloatField): Rating score from Metacritic.
        genre (ManyToManyField): The genre(s) associated with this game.
        added_by (Foreign Key): Username of who added the game.
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
    cover_image = models.ImageField(upload_to='games/covers')
    metacritic_score = models.FloatField()
    genres = models.ManyToManyField(Genre, related_name='games')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_games',
    )
    slug = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True, blank=True)

    def get_absolute_url(self):
        return reverse('catalog:game_detail', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f'{self.title} {self.release_year}'



class Character(models.Model):
    """Represents a fictional character appearing in a video game.

    Attributes:
        name (CharField): The name of the character (max length: 150).
        description (TextField): A brief bio of the character.
        game (ForeignKey): The Game model instance this character belongs to.
        photo (ImageField): An image file of the character, stored in
            'characters/photos/'.
        slug (SlugField): Unique URL identifier containing only Latin letters,
            numbers, hyphens, and underscores.
    """

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    game = models.ForeignKey(
        'Game',
        on_delete=models.PROTECT,
        related_name='characters',
    )
    photo = models.ImageField(upload_to='characters/photos/')
    slug = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True, blank=True)

    def get_absolute_url(self):
        return reverse('catalog:character_detail', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugable_field_name='name')
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Quest(models.Model):
    """Represents an in-game quest or objective associated with a game.

    Attributes:
        title (CharField): The title or name of the quest (max length: 120).
        description (TextField): Detailed description of the quest objective.
        game (ForeignKey): The Game model instance this quest belongs to.
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
