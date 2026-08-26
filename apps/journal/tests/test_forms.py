import pytest

from apps.catalog.models import Character, Game
from apps.journal.forms import JournalEntryForm
from apps.journal.models import FavoriteCharacter, UserJournal

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='spiderman', password='testpass123')


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(username='batman', password='testpass123')


@pytest.fixture
def game():
    return Game.objects.create(
        title='Portal 2',
        description='A puzzle-platform game.',
        release_year=2011,
        publisher='Valve',
        metacritic_score=95,
    )


@pytest.fixture
def other_game():
    return Game.objects.create(
        title="Baldur's Gate 3",
        description='An RPG based on Dungeons & Dragons.',
        release_year=2023,
        publisher='Larian Studios',
        metacritic_score=96,
    )


@pytest.fixture
def character(game):
    return Character.objects.create(
        name='GLaDOS',
        description='An AI antagonist.',
        game=game,
    )


class TestJournalEntryFormFavoriteCharactersInitial:

    def test_create_has_empty_initial(self, user, game):
        """На create (без instance) initial пустой — избранных ещё нет и не может быть."""
        form = JournalEntryForm(game=game, user=user)
        assert list(form.fields['favorite_characters'].initial) == []

    def test_update_shows_existing_favorites(self, user, game, character):
        """На update initial содержит реально избранных персонажей пользователя."""
        journal = UserJournal.objects.create(user=user, game=game)
        FavoriteCharacter.objects.create(user=user, character=character)

        form = JournalEntryForm(instance=journal)

        assert list(form.fields['favorite_characters'].initial) == [character]

    def test_favorites_from_other_game_are_excluded(self, user, game, other_game, character):
        """Избранный персонаж из другой игры не должен попадать в initial."""
        journal = UserJournal.objects.create(user=user, game=game)
        foreign_character = Character.objects.create(name='Astarion', game=other_game)
        FavoriteCharacter.objects.create(user=user, character=foreign_character)

        form = JournalEntryForm(instance=journal)

        assert foreign_character not in form.fields['favorite_characters'].initial

    def test_favorites_of_other_user_are_excluded(self, user, other_user, game, character):
        """Избранный персонаж другого пользователя не должен попадать в initial."""
        journal = UserJournal.objects.create(user=user, game=game)
        FavoriteCharacter.objects.create(user=other_user, character=character)

        form = JournalEntryForm(instance=journal)

        assert list(form.fields['favorite_characters'].initial) == []