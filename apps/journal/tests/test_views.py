"""
Full test suite for apps/journal/views.py
Coverage: all 10 view classes across happy paths, auth/permission guards,
edge cases, and redirect targets.

Fixtures are defined in conftest.py style within this file using pytest
fixtures for portability. Adjust import paths to match your project layout.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.catalog.models import Character, Game, Genre, Quest
from apps.journal.models import Comment, FavoriteCharacter, UserJournal

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def journal_url(name, **kwargs):
    return reverse(f'journal:{name}', kwargs=kwargs)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def genre(db):
    return Genre.objects.create(name='RPG')


@pytest.fixture
def game(db, genre):
    g = Game(
        title='Test Game',
        description='A great game',
        release_year=2020,
        publisher='Pub',
        metacritic_score=85.0,
        cover_image='catalog/games/covers/test.jpg',  # ← фиктивный путь
    )
    g.save()
    g.genres.add(genre)
    return g


@pytest.fixture
def character(db, game):
    c = Character(
        name='Hero',
        description='The protagonist',
        game=game,
    )
    c.save()
    return c


@pytest.fixture
def quest(db, game):
    return Quest.objects.create(
        title='Main Quest',
        description='Finish the game',
        game=game,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='alice', password='pass', email='alice@example.com'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='bob', password='pass', email='bob@example.com'
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username='admin', password='pass', email='admin@example.com'
    )


@pytest.fixture
def journal_entry(db, user, game):
    """A minimal journal entry — no review yet (not a 'post')."""
    return UserJournal.objects.create(
        user=user,
        game=game,
        status=UserJournal.GameStatus.PLANNED,
    )


@pytest.fixture
def journal_post(db, user, game):
    """A journal entry with a review (visible to public)."""
    return UserJournal.objects.create(
        user=user,
        game=game,
        status=UserJournal.GameStatus.COMPLETED,
        review='Fantastic game!',
    )


@pytest.fixture
def comment(db, journal_post, other_user):
    return Comment.objects.create(
        journal_entry=journal_post,
        author=other_user,
        text='Great review!',
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def other_client(client, other_user):
    client.force_login(other_user)
    return client


@pytest.fixture
def super_client(client, superuser):
    client.force_login(superuser)
    return client


# ---------------------------------------------------------------------------
# GameStatusQuickView
# ---------------------------------------------------------------------------

class TestGameStatusQuickView:

    def url(self, game):
        return journal_url('game_status_quick', game_slug=game.slug)

    @pytest.mark.django_db
    def test_creates_journal_entry_if_not_exists(self, auth_client, game, user):
        assert not UserJournal.objects.filter(user=user, game=game).exists()
        auth_client.post(self.url(game), {'status': 'planned'})
        assert UserJournal.objects.filter(user=user, game=game).exists()

    @pytest.mark.django_db
    def test_updates_existing_journal_entry(self, auth_client, game, journal_entry):
        assert journal_entry.status == UserJournal.GameStatus.PLANNED
        auth_client.post(self.url(game), {'status': 'completed'})
        journal_entry.refresh_from_db()
        assert journal_entry.status == UserJournal.GameStatus.COMPLETED

    @pytest.mark.django_db
    def test_redirects_to_game_detail(self, auth_client, game):
        response = auth_client.post(self.url(game), {'status': 'planned'})
        assert response.status_code == 302
        assert response['Location'] == game.get_absolute_url()

    @pytest.mark.django_db
    def test_invalid_status_redirects_with_error(self, auth_client, game):
        response = auth_client.post(self.url(game), {'status': 'INVALID'})
        assert response.status_code == 302
        assert response['Location'] == game.get_absolute_url()

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(self, client, game):
        response = client.post(self.url(game), {'status': 'planned'})
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_404_for_unknown_game(self, auth_client):
        response = auth_client.post(
            journal_url('game_status_quick', game_slug='no-such-game'),
            {'status': 'planned'},
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# UserJournalListView
# ---------------------------------------------------------------------------

class TestUserJournalListView:

    def url(self, username):
        return journal_url('journal_list', username=username)

    @pytest.mark.django_db
    def test_shows_only_posts_for_other_users(
        self, client, user, journal_entry, journal_post
    ):
        """Anonymous/other visitors see only entries that have a review."""
        response = client.get(self.url(user.username))
        assert response.status_code == 200
        qs = response.context['object_list']
        assert journal_post in qs
        assert journal_entry not in qs

    @pytest.mark.django_db
    def test_profile_user_in_context(self, client, user):
        response = client.get(self.url(user.username))
        assert response.context['profile_user'] == user

    @pytest.mark.django_db
    def test_404_for_unknown_user(self, client):
        response = client.get(self.url('nobody'))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_pagination(self, client, user, game, genre):
        """Creates 6 posts; page size is 5, so page 2 should have 1 entry."""
        for i in range(6):
            g = Game(
                title=f'Game {i}',
                description='x',
                release_year=2020,
                publisher='Pub',
                metacritic_score=70.0,
            )
            g.save()
            g.genres.add(genre)
            UserJournal.objects.create(
                user=user, game=g, review='Review', status='completed'
            )
        response = client.get(self.url(user.username) + '?page=2')
        assert response.status_code == 200
        assert len(response.context['object_list']) == 1


# ---------------------------------------------------------------------------
# UserJournalDetailView
# ---------------------------------------------------------------------------

class TestUserJournalDetailView:

    def url(self, username, game_slug):
        return journal_url(
            'journal_entry_detail', username=username, game_slug=game_slug
        )

    @pytest.mark.django_db
    def test_owner_can_see_own_entry_without_review(
        self, auth_client, user, game, journal_entry
    ):
        response = auth_client.get(self.url(user.username, game.slug))
        assert response.status_code == 200
        assert response.context['object'] == journal_entry

    @pytest.mark.django_db
    def test_public_can_see_entry_with_review(
        self, client, user, game, journal_post
    ):
        response = client.get(self.url(user.username, game.slug))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_public_cannot_see_entry_without_review(
        self, client, user, game, journal_entry
    ):
        response = client.get(self.url(user.username, game.slug))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_game_in_context(self, auth_client, user, game, journal_entry):
        response = auth_client.get(self.url(user.username, game.slug))
        assert response.context['game'] == game

    @pytest.mark.django_db
    def test_favorite_characters_in_context(
        self, auth_client, user, game, journal_entry, character
    ):
        FavoriteCharacter.objects.create(user=user, character=character)
        response = auth_client.get(self.url(user.username, game.slug))
        fav_chars = list(response.context['favorite_characters'])
        assert len(fav_chars) == 1
        assert fav_chars[0].character == character

    @pytest.mark.django_db
    def test_404_for_unknown_entry(self, auth_client, user):
        response = auth_client.get(self.url(user.username, 'ghost-game'))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# UserJournalDeleteView
# ---------------------------------------------------------------------------

class TestUserJournalDeleteView:

    def url(self, username, game_slug):
        return journal_url(
            'journal_entry_delete', username=username, game_slug=game_slug
        )

    @pytest.mark.django_db
    def test_owner_can_delete(self, auth_client, user, game, journal_entry):
        response = auth_client.post(self.url(user.username, game.slug))
        assert response.status_code == 302
        assert not UserJournal.objects.filter(pk=journal_entry.pk).exists()

    @pytest.mark.django_db
    def test_delete_redirects_to_journal_list(
        self, auth_client, user, game, journal_entry
    ):
        response = auth_client.post(self.url(user.username, game.slug))
        assert response['Location'] == journal_url(
            'journal_list', username=user.username
        )

    @pytest.mark.django_db
    def test_non_owner_cannot_delete(
        self, other_client, user, game, journal_entry
    ):
        response = other_client.post(self.url(user.username, game.slug))
        # redirected away, entry still exists
        assert response.status_code == 302
        assert UserJournal.objects.filter(pk=journal_entry.pk).exists()

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(
        self, client, user, game, journal_entry
    ):
        response = client.post(self.url(user.username, game.slug))
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_get_shows_confirmation_page(
        self, auth_client, user, game, journal_entry
    ):
        response = auth_client.get(self.url(user.username, game.slug))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_404_for_unknown_entry(self, auth_client, user):
        response = auth_client.post(self.url(user.username, 'ghost-game'))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# CommentCreateView
# ---------------------------------------------------------------------------

class TestCommentCreateView:

    def url(self, username, game_slug):
        return journal_url(
            'comment_create', username=username, game_slug=game_slug
        )

    @pytest.mark.django_db
    def test_creates_comment(
        self, other_client, user, game, journal_post, other_user
    ):
        other_client.post(
            self.url(user.username, game.slug), {'text': 'Nice!'}
        )
        assert Comment.objects.filter(
            journal_entry=journal_post, author=other_user, text='Nice!'
        ).exists()

    @pytest.mark.django_db
    def test_sets_author_from_request(
        self, other_client, user, game, journal_post, other_user
    ):
        other_client.post(
            self.url(user.username, game.slug), {'text': 'Hello'}
        )
        comment = Comment.objects.get(journal_entry=journal_post)
        assert comment.author == other_user

    @pytest.mark.django_db
    def test_sets_journal_entry_from_url(
        self, other_client, user, game, journal_post
    ):
        other_client.post(
            self.url(user.username, game.slug), {'text': 'Hi'}
        )
        comment = Comment.objects.get(journal_entry=journal_post)
        assert comment.journal_entry == journal_post

    @pytest.mark.django_db
    def test_redirects_after_comment(
        self, other_client, user, game, journal_post
    ):
        response = other_client.post(
            self.url(user.username, game.slug), {'text': 'Cool'}
        )
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(
        self, client, user, game, journal_post
    ):
        response = client.post(
            self.url(user.username, game.slug), {'text': 'Hi'}
        )
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_comment_on_invisible_entry_returns_404(
        self, other_client, user, game, journal_entry
    ):
        """other_user can't comment on alice's private entry (no review)."""
        response = other_client.post(
            self.url(user.username, game.slug), {'text': 'Hi'}
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_empty_text_does_not_create_comment(
        self, other_client, user, game, journal_post
    ):
        other_client.post(self.url(user.username, game.slug), {'text': ''})
        assert not Comment.objects.filter(journal_entry=journal_post).exists()


# ---------------------------------------------------------------------------
# CommentDeleteView
# ---------------------------------------------------------------------------

class TestCommentDeleteView:

    def url(self, pk):
        return journal_url('comment_delete', pk=pk)

    @pytest.mark.django_db
    def test_author_can_delete_own_comment(
        self, other_client, comment
    ):
        response = other_client.post(self.url(comment.pk))
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    @pytest.mark.django_db
    def test_journal_owner_can_delete_comment(
        self, auth_client, comment
    ):
        """alice owns the journal; she can delete bob's comment."""
        response = auth_client.post(self.url(comment.pk))
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    @pytest.mark.django_db
    def test_superuser_can_delete_any_comment(
        self, super_client, comment
    ):
        response = super_client.post(self.url(comment.pk))
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    @pytest.mark.django_db
    def test_unrelated_user_cannot_delete(
        self, db, client, comment
    ):
        """A third user (not author, not journal owner, not superuser)."""
        third = User.objects.create_user(username='eve', password='pass')
        client.force_login(third)
        response = client.post(self.url(comment.pk))
        # OwnerRequiredMixin redirects non-owners
        assert response.status_code == 302
        assert Comment.objects.filter(pk=comment.pk).exists()

    @pytest.mark.django_db
    def test_redirects_to_journal_entry_after_delete(
        self, other_client, comment
    ):
        response = other_client.post(self.url(comment.pk))
        assert response['Location'] == comment.journal_entry.get_absolute_url()

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(self, client, comment):
        response = client.post(self.url(comment.pk))
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_404_for_nonexistent_comment(self, auth_client):
        response = auth_client.post(self.url(9999))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# FavoriteCharacterToggleView
# ---------------------------------------------------------------------------

class TestFavoriteCharacterToggleView:

    def url(self, character_slug):
        return journal_url('favorite_toggle', character_slug=character_slug)

    @pytest.mark.django_db
    def test_adds_character_to_favorites(
        self, auth_client, character, user
    ):
        assert not FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()
        auth_client.post(self.url(character.slug))
        assert FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()

    @pytest.mark.django_db
    def test_removes_character_from_favorites(
        self, auth_client, character, user
    ):
        FavoriteCharacter.objects.create(user=user, character=character)
        auth_client.post(self.url(character.slug))
        assert not FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()

    @pytest.mark.django_db
    def test_redirects_to_character_page(self, auth_client, character):
        response = auth_client.post(self.url(character.slug))
        assert response.status_code == 302
        assert response['Location'] == character.get_absolute_url()

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(self, client, character):
        response = client.post(self.url(character.slug))
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_404_for_unknown_character(self, auth_client):
        response = auth_client.post(self.url('no-one'))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_toggle_is_idempotent(self, auth_client, character, user):
        """Toggle twice → character ends up not favorited."""
        auth_client.post(self.url(character.slug))
        auth_client.post(self.url(character.slug))
        assert not FavoriteCharacter.objects.filter(
            user=user, character=character
        ).exists()


# ---------------------------------------------------------------------------
# FavoriteCharacterShowcaseToggleView
# ---------------------------------------------------------------------------

class TestFavoriteCharacterShowcaseToggleView:

    def url(self, character_slug):
        return journal_url(
            'favorite_showcase_toggle', character_slug=character_slug
        )

    @pytest.fixture
    def favorite(self, db, user, character):
        return FavoriteCharacter.objects.create(
            user=user, character=character, is_on_showcase=False
        )

    @pytest.mark.django_db
    def test_toggles_showcase_on(self, auth_client, character, favorite):
        auth_client.post(self.url(character.slug))
        favorite.refresh_from_db()
        assert favorite.is_on_showcase is True

    @pytest.mark.django_db
    def test_toggles_showcase_off(self, auth_client, character, user):
        fav = FavoriteCharacter.objects.create(
            user=user, character=character, is_on_showcase=True
        )
        auth_client.post(self.url(character.slug))
        fav.refresh_from_db()
        assert fav.is_on_showcase is False

    @pytest.mark.django_db
    def test_redirects_to_profile(self, auth_client, character, user, favorite):
        response = auth_client.post(self.url(character.slug))
        assert response.status_code == 302
        assert response['Location'] == reverse(
            'journal:journal_list', kwargs={'username': user.username}
        )

    @pytest.mark.django_db
    def test_404_if_not_favorited(self, auth_client, character):
        """Can't showcase a character that isn't favorited first."""
        response = auth_client.post(self.url(character.slug))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(self, client, character):
        response = client.post(self.url(character.slug))
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_other_user_cannot_toggle_others_showcase(
        self, other_client, character, user, favorite
    ):
        """bob tries to toggle alice's showcase entry → 404 (not his fav)."""
        response = other_client.post(self.url(character.slug))
        assert response.status_code == 404
        favorite.refresh_from_db()
        assert favorite.is_on_showcase is False


# ---------------------------------------------------------------------------
# UserJournalCreateView — form-level smoke test
# (formsets require multipart; we test auth guard and GET render)
# ---------------------------------------------------------------------------

class TestUserJournalCreateView:

    def url(self, username):
        return journal_url('journal_entry_create', username=username)

    @pytest.mark.django_db
    def test_get_renders_form(self, auth_client, user, game):
        url = reverse(
            'journal:journal_entry_create',
            kwargs={'username': user.username, 'game_slug': game.slug}
        )
        response = auth_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(self, client, user, game):
        url = reverse(
            'journal:journal_entry_create',
            kwargs={'username': user.username, 'game_slug': game.slug}
        )
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_404_if_game_does_not_exist(self, auth_client, user):
        url = reverse(
            'journal:journal_entry_create',
            kwargs={'username': user.username, 'game_slug': 'nonexistent'}
        )
        response = auth_client.get(url)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# UserJournalUpdateView
# ---------------------------------------------------------------------------

class TestUserJournalUpdateView:

    def url(self, username, game_slug):
        return journal_url(
            'journal_entry_edit', username=username, game_slug=game_slug
        )

    @pytest.mark.django_db
    def test_owner_can_access_edit_form(
        self, auth_client, user, game, journal_entry
    ):
        response = auth_client.get(self.url(user.username, game.slug))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_non_owner_is_redirected(
        self, other_client, user, game, journal_entry
    ):
        response = other_client.get(self.url(user.username, game.slug))
        assert response.status_code == 302
        # OwnerRequiredMixin sends non-owners to the object's own URL
        assert response['Location'] == journal_entry.get_absolute_url()

    @pytest.mark.django_db
    def test_unauthenticated_redirects_to_login(
        self, client, user, game, journal_entry
    ):
        response = client.get(self.url(user.username, game.slug))
        assert response.status_code == 302
        assert '/login/' in response['Location'] or '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_404_for_unknown_entry(self, auth_client, user):
        response = auth_client.get(self.url(user.username, 'ghost-game'))
        assert response.status_code == 404