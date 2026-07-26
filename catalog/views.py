"""
Views for the catalog application.

This module contains class-based views for listing, creating, retrieving,
updating, and deleting Game and Character objects. It also includes custom
mixins for access control and database query optimization.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CharacterForm, GameForm
from .models import Character, Game

GAMES_PER_PAGE = 15
CHARACTERS_PER_PAGE = 20


class AuthorAssignmentMixin:
    """Assigns the current user as the author before saving the object."""

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class AuthorOrSuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that verifies the current user is either the author of the object
    or a superuser.

    Overrides `get_object` to cache the retrieved instance. By default, combining
    `UserPassesTestMixin` with Django's generic editing views (`UpdateView`,
    `DeleteView`) results in redundant database queries. The object is queried once
    during the permission check in `test_func()`, and then a second time either by
    the view's `get`/`post` methods (if access is granted) or by `handle_no_permission()`
    (to resolve the redirect URL if access is denied). Caching the object ensures
    only a single database query is executed per request lifecycle.
    """

    def get_object(self, queryset=None):
        """
        Retrieves the object and caches it on the instance to prevent 
        duplicate database queries during the view's lifecycle.
        """
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        """
        Checks if the current user is the author of the object or a superuser.
        """
        target_object = self.get_object()
        return (target_object.added_by == self.request.user) or self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Redirects unauthorized users to the object's detail page instead 
        of showing a 403 Forbidden error.
        """
        return redirect(self.get_object().get_absolute_url())


class GamesListView(ListView):
    """
    Displays a paginated list of all games in the catalog.
    """
    model = Game
    paginate_by = GAMES_PER_PAGE
    template_name = 'catalog/games.html'


class CharactersListView(ListView):
    """
    Displays a paginated list of all characters in the catalog.
    """
    model = Character
    paginate_by = CHARACTERS_PER_PAGE
    template_name = 'catalog/characters.html'


class GameDetailView(DetailView):
    """
    Displays the details of a single game, including its related 
    characters and quests.
    """
    model = Game
    template_name = 'catalog/game_detail.html'

    def get_queryset(self):
        """
        Optimizes database queries by prefetching related characters 
        and quests.
        """
        return super().get_queryset().prefetch_related('characters', 'quests')

    def get_context_data(self, **kwargs):
        """
        Adds related characters and quests to the template context.
        """
        context = super().get_context_data(**kwargs)
        context['characters'] = self.object.characters.all()
        context['quests'] = self.object.quests.all()
        return context


class CharacterDetailView(DetailView):
    """
    Displays the details of a single character.
    """
    model = Character
    template_name = 'catalog/character_detail.html'


class GameCreateView(LoginRequiredMixin, AuthorAssignmentMixin, CreateView):
    """
    Displays a form to create a new game and handles its submission.
    Requires the user to be logged in.
    """
    model = Game
    form_class = GameForm
    template_name = 'catalog/add_game.html'


class CharacterCreateView(LoginRequiredMixin, CreateView, AuthorAssignmentMixin):
    """
    Displays a form to create a new character and handles its submission.
    Requires the user to be logged in.
    """
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/add_character.html'


class GameUpdateView(AuthorOrSuperuserRequiredMixin, UpdateView):
    """
    Displays a form to update an existing game.
    Only accessible by the game's author or a superuser.
    """
    model = Game
    form_class = GameForm
    template_name = 'catalog/add_game.html'


class CharacterUpdateView(AuthorOrSuperuserRequiredMixin, UpdateView):
    """
    Displays a form to update an existing character.
    Only accessible by the character's author or a superuser.
    """
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/add_character.html'


class GameDeleteView(AuthorOrSuperuserRequiredMixin, DeleteView):
    """
    Displays a confirmation page to delete an existing game.
    Only accessible by the game's author or a superuser.
    """
    model = Game
    template_name = 'catalog/game_confirm_delete.html'

    def get_success_url(self):
        """
        Redirects the user to the games list upon successful deletion.
        """
        return reverse('catalog:games')


class CharacterDeleteView(AuthorOrSuperuserRequiredMixin, DeleteView):
    """
    Displays a confirmation page to delete an existing character.
    Only accessible by the character's author or a superuser.
    """
    model = Character
    template_name = 'catalog/character_confirm_delete.html'

    def get_success_url(self):
        """
        Redirects the user to the characters list upon successful deletion.
        """
        return reverse('catalog:characters')
