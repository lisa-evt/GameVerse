from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from smart_selects.db_fields import ChainedManyToManyField

from .querysets import UserJournalQuerySet

STATUS_MAX_CHAR_LENGTH = 11
MAX_QUOTE_LENGTH = 250


class CreatedAtModel(models.Model):
    """An abstract base model that provides a self-updating creation timestamp.

    Attributes:
        created_at (DateTimeField): The timestamp when the object was created.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UserJournal(CreatedAtModel):
    """Represents a user's tracking entry and personal review for a video game.

    Attributes:
        user (ForeignKey): The user who owns this journal entry.
        game (ForeignKey): The game being tracked in this journal entry.
        status (CharField): The current completion status of the game choices
            from GameStatus.
        favorite_quests (ManyToManyField): The quest(s) marked as favorites by
            the user for this journal entry.
        review (TextField, optional): Personal review or thoughts on the game.
        personal_rating (FloatField, optional): User's custom rating.
        is_on_showcase (BooleanField): Whether this game is highlighted on the
            user's profile showcase.
        completed_date (DateField, optional): Date when the game was completed.
        created_at (DateTimeField): When the journal entry was created.
    """

    class GameStatus(models.TextChoices):
        """Enumeration of possible game playthrough statuses."""

        PLANNED = 'planned'
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'
        DROPPED = 'dropped'
        ON_HOLD = 'on_hold'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='journal',
        on_delete=models.PROTECT
    )
    game = models.ForeignKey(
        'catalog.Game',
        on_delete=models.PROTECT,
        related_name='journal',
    )
    status = models.CharField(
        max_length=STATUS_MAX_CHAR_LENGTH,
        choices=GameStatus,
        default=GameStatus.PLANNED
    )
    favorite_quests = ChainedManyToManyField(
        'catalog.Quest',
        chained_field='game',
        chained_model_field='game',
        related_name='favorited_in',
        blank=True,
    )
    review = models.TextField(null=True, blank=True)
    personal_rating = models.FloatField(null=True, blank=True)
    is_on_showcase = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserJournalQuerySet.as_manager()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('game', 'user'),
                name='users_journal'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.game} ({self.status})'


class Screenshot(models.Model):
    """Represents a screenshot uploaded by a user for a specific journal entry.

    Attributes:
        screenshot (ImageField): Image file of the screenshot, stored in
            'journal/screenshots/'.
        caption (TextField, optional): Optional description or caption for
            the screenshot.
        user_journal_entry (ForeignKey): The user's journal entry this
            screenshot belongs to.
    """

    screenshot = models.ImageField(upload_to='journal/screenshots')
    caption = models.TextField(null=True, blank=True)
    user_journal_entry = models.ForeignKey(
        UserJournal,
        related_name='screenshots',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return the string representation of the screenshot.

        Returns:
            str: A label indicating the journal entry and screenshot ID.
        """
        return f'Screenshot for {self.user_journal_entry_id} ({self.pk})'


class FavoriteQuote(models.Model):
    """Represents a memorable quote, saved in a journal entry.

    Attributes:
        quote (CharField): The text of the character quote.
        character (ForeignKey): The game character who said the quote.
        user_journal_entry (ForeignKey): The journal entry this quote is saved.
    """
    quote = models.CharField(max_length=MAX_QUOTE_LENGTH)
    character = models.ForeignKey(
        'catalog.Character',
        related_name='quotes',
        on_delete=models.PROTECT,
    )
    user_journal_entry = models.ForeignKey(
        'UserJournal',
        related_name='favorite_quotes',
        on_delete=models.CASCADE,
    )

    def clean(self):
        """Validate that the character belongs to the same game
            as the journal entry.

        Raises:
            ValidationError:
            If the character's game does not match the journal entry's game.
        """
        if self.character.game != self.user_journal_entry.game:
            raise ValidationError(
                'Character must belong to the same game as the journal entry.'
            )

    def __str__(self):
        return f'"{self.quote}" - {self.character}'


class FavoriteCharacter(models.Model):
    """Represents a game character favorited by a user.

    Attributes:
        user (ForeignKey): The user who favorited the character.
        character (ForeignKey): The character that was favorited.
        is_on_showcase (BooleanField): Whether this character
            is highlighted on the user's profile showcase.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='favorite_characters',
        on_delete=models.PROTECT
    )
    character = models.ForeignKey(
        'catalog.Character',
        related_name='favorited_by_users',
        on_delete=models.PROTECT,
    )
    is_on_showcase = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('character', 'user'),
                name='users_favorite_characters'
            )
        ]

    def __str__(self):
        return f'{self.user} favorited {self.character}'


class Comment(CreatedAtModel):
    """Represents a comment made by a user on a journal entry.

    Attributes:
        journal_entry (ForeignKey): The user journal entry being commented on.
        author (ForeignKey): The user who authored the comment.
        text (TextField): The body content of the comment.
        created_at (DateTimeField): Timestamp inherited from CreatedAtModel.
    """
    journal_entry = models.ForeignKey(
        'UserJournal',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_comments',
    )
    text = models.TextField()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.author}: {self.text[:30]}"
