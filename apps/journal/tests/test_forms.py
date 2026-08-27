import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.catalog.models import Character, Game, Quest
from apps.journal.forms import (CommentForm, FavoriteQuoteForm, GameStatusForm,
                                JournalEntryForm, QuoteFormSet, ScreenshotForm,
                                ScreenshotFormSet)
from apps.journal.models import (FavoriteCharacter, FavoriteQuote, Screenshot,
                                 UserJournal)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='spiderman',
        password='testpass123'
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username='batman',
        password='testpass123'
    )


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


@pytest.fixture
def other_character(other_game):
    return Character.objects.create(
        name='Astarion', description='A vampire spawn.', game=other_game,
    )


@pytest.fixture
def quest(game):
    return Quest.objects.create(
        title='The Cake Is a Lie',
        description='Reach the cake.',
        game=game
    )


@pytest.fixture
def other_quest(other_game):
    return Quest.objects.create(
        title='Save the city',
        description='...',
        game=other_game
    )


@pytest.fixture
def journal(user, game):
    return UserJournal.objects.create(user=user, game=game)


@pytest.fixture
def tiny_image():
    content = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return SimpleUploadedFile('test.png', content, content_type='image/png')

# --- FavoriteQuoteForm -------------------------------------------------


class TestFavoriteQuoteForm:

    def test_missing_game_raises_valueerror(self):
        with pytest.raises(ValueError, match="requires 'game'"):
            FavoriteQuoteForm()

    def test_character_queryset_filtered_by_game(
            self, game, character, other_character
    ):
        form = FavoriteQuoteForm(game=game)
        assert list(form.fields['character'].queryset) == [character]
        assert other_character not in form.fields['character'].queryset

    def test_character_from_other_game_is_invalid(self, game, other_character):
        form = FavoriteQuoteForm(
            data={'quote': 'Test quote', 'character': other_character.id},
            game=game,
        )
        assert not form.is_valid()
        assert 'character' in form.errors

    def test_valid_data_is_valid(self, game, character):
        form = FavoriteQuoteForm(
            data={'quote': 'The cake is a lie.', 'character': character.pk},
            game=game,
        )
        assert form.is_valid(), form.errors


# --- ScreenshotForm ------------------------------------------------------

class TestScreenshotForm:

    def test_valid_data(self, tiny_image):
        form = ScreenshotForm(
            data={'caption': 'Nice view'},
            files={'screenshot': tiny_image},
        )
        assert form.is_valid(), form.errors

    def test_screenshot_is_required(self):
        form = ScreenshotForm(data={'caption': 'Missing image'})
        assert not form.is_valid()
        assert 'screenshot' in form.errors


# --- GameStatusForm --------------------------------------------------

class TestGameStatusForm:

    def test_valid_status(self):
        form = GameStatusForm(data={'status': UserJournal.GameStatus.PLANNED})
        assert form.is_valid(), form.errors

    def test_only_status_field_present(self):
        form = GameStatusForm()
        assert list(form.fields.keys()) == ['status']

    def test_invalid_status_choice_is_invalid(self):
        form = GameStatusForm(data={'status': 'not_a_real_status'})
        assert not form.is_valid()
        assert 'status' in form.errors


# --- JournalEntryForm: __init__ ---------------------------------------

class TestJournalEntryFormInit:

    def test_missing_user_and_game_raises(self):
        with pytest.raises(UserJournal.user.RelatedObjectDoesNotExist):
            JournalEntryForm()

    def test_favorite_characters_queryset_filtered_by_game(
        self, user, game, character, other_character,
    ):
        form = JournalEntryForm(user=user, game=game)
        assert list(form.fields['favorite_characters'].queryset) == [character]

    def test_favorite_quests_queryset_filtered_by_game(
        self, user, game, quest, other_quest,
    ):
        form = JournalEntryForm(user=user, game=game)
        assert list(form.fields['favorite_quests'].queryset) == [quest]


# --- JournalEntryForm: initial -----------------------------------------

class TestJournalEntryFormFavoriteCharactersInitial:

    def test_create_has_empty_initial(self, user, game):
        form = JournalEntryForm(game=game, user=user)
        assert list(form.fields['favorite_characters'].initial) == []

    def test_update_shows_existing_favorites(self, user, game, character):
        journal = UserJournal.objects.create(user=user, game=game)
        FavoriteCharacter.objects.create(user=user, character=character)

        form = JournalEntryForm(instance=journal)

        assert list(form.fields['favorite_characters'].initial) == [character]

    def test_favorites_from_other_game_are_excluded(
        self, user, game, other_game, character,
    ):
        journal = UserJournal.objects.create(user=user, game=game)
        foreign_character = Character.objects.create(
            name='Astarion', description='...', game=other_game,
        )
        FavoriteCharacter.objects.create(
            user=user,
            character=foreign_character
        )

        form = JournalEntryForm(instance=journal)

        chars_initial = form.fields['favorite_characters'].initial
        assert foreign_character not in chars_initial

    def test_favorites_of_other_user_are_excluded(
        self, user, other_user, game, character,
    ):
        journal = UserJournal.objects.create(user=user, game=game)
        FavoriteCharacter.objects.create(user=other_user, character=character)

        form = JournalEntryForm(instance=journal)

        assert list(form.fields['favorite_characters'].initial) == []


# --- JournalEntryForm: save() -----------------------------------------

class TestJournalEntryFormSave:

    def _valid_data(self, character):
        return {
            'status': UserJournal.GameStatus.COMPLETED,
            'personal_rating': 9,
            'is_on_showcase': False,
            'favorite_characters': [character.pk],
            'favorite_quests': [],
        }

    def test_save_syncs_favorite_characters(self, user, game, character):
        form = JournalEntryForm(
            data=self._valid_data(character),
            user=user,
            game=game
        )
        form.instance.user = user
        form.instance.game = game
        assert form.is_valid(), form.errors

        form.save()

        assert FavoriteCharacter.objects.filter(
            user=user, character=character,
        ).exists()

    def test_save_commit_false_does_not_sync_favorites(
            self, user, game, character
    ):
        form = JournalEntryForm(
            data=self._valid_data(character),
            user=user,
            game=game
        )
        form.instance.user = user
        form.instance.game = game
        assert form.is_valid(), form.errors

        form.save(commit=False)

        assert not FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()

    def test_save_removes_unselected_favorite(self, user, game, character):
        FavoriteCharacter.objects.create(user=user, character=character)
        journal = UserJournal.objects.create(user=user, game=game)

        data = self._valid_data(character)
        data['favorite_characters'] = []  # снимаем персонажа с избранного
        form = JournalEntryForm(data=data, instance=journal)
        assert form.is_valid(), form.errors

        form.save()

        assert not FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()


# --- CommentForm ----------------------------------------------------

class TestCommentForm:

    def test_valid_text(self):
        form = CommentForm(data={'text': 'Great review!'})
        assert form.is_valid(), form.errors

    def test_empty_text_is_invalid(self):
        form = CommentForm(data={'text': ''})
        assert not form.is_valid()
        assert 'text' in form.errors


# --- QuoteFormSet ------------------------------------------------------

class TestQuoteFormSet:

    def test_requires_game_in_form_kwargs(self):
        with pytest.raises(ValueError, match="requires 'game'"):
            QuoteFormSet()

    def test_saves_quote_linked_to_journal(self, journal, game, character):
        empty_formset = QuoteFormSet(
            instance=journal, form_kwargs={'game': game}
        )
        prefix = empty_formset.prefix

        data = {
            f'{prefix}-TOTAL_FORMS': '1',
            f'{prefix}-INITIAL_FORMS': '0',
            f'{prefix}-MIN_NUM_FORMS': '0',
            f'{prefix}-MAX_NUM_FORMS': '1000',
            f'{prefix}-0-quote': 'The cake is a lie.',
            f'{prefix}-0-character': character.pk,
        }
        formset = QuoteFormSet(
            data, instance=journal, form_kwargs={'game': game}
        )
        assert formset.is_valid(), formset.errors

        formset.save()

        assert FavoriteQuote.objects.filter(
            quote='The cake is a lie.'
        ).exists()


# --- ScreenshotFormSet -------------------------------------------------

class TestScreenshotFormSet:

    def test_saves_screenshot_linked_to_journal(self, journal, tiny_image):
        empty_formset = ScreenshotFormSet(instance=journal)
        prefix = empty_formset.prefix

        data = {
            f'{prefix}-TOTAL_FORMS': '1',
            f'{prefix}-INITIAL_FORMS': '0',
            f'{prefix}-MIN_NUM_FORMS': '0',
            f'{prefix}-MAX_NUM_FORMS': '1000',
            f'{prefix}-0-caption': 'Nice shot',
        }
        files = {f'{prefix}-0-screenshot': tiny_image}
        formset = ScreenshotFormSet(data, files, instance=journal)
        assert formset.is_valid(), formset.errors

        formset.save()

        assert Screenshot.objects.filter(caption='Nice shot').exists()