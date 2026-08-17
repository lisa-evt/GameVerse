"""
Views for the catalog application.

This module contains class-based views for listing, creating, retrieving,
updating, and deleting Game and Character objects. It also includes custom
mixins for access control and database query optimization.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CharacterForm, GameForm
from .models import Character, Game
from .mixins import AuthorAssignmentMixin, AuthorOrSuperuserRequiredMixin

GAMES_PER_PAGE = 15
CHARACTERS_PER_PAGE = 20


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
        if self.object.added_by == self.request.user:
            context['edit_url'] = reverse('catalog:game_edit', args=[self.object.slug])
            context['delete_url'] = reverse('catalog:game_delete', args=[self.object.slug])
        return context


class CharacterDetailView(DetailView):
    """
    Displays the details of a single character.
    """
    model = Character
    template_name = 'catalog/character_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.added_by == self.request.user:
            context['edit_url'] = reverse('catalog:character_edit', args=[self.object.slug])
            context['delete_url'] = reverse('catalog:character_delete', args=[self.object.slug])
        return context


class GameCreateView(AuthorAssignmentMixin, CreateView):
    """
    Displays a form to create a new game and handles its submission.
    Requires the user to be logged in.
    """
    model = Game
    form_class = GameForm
    template_name = 'catalog/game_add.html'


class CharacterCreateView(AuthorAssignmentMixin, CreateView):
    """
    Displays a form to create a new character and handles its submission.
    Requires the user to be logged in.
    """
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/character_add.html'


class GameUpdateView(AuthorOrSuperuserRequiredMixin, UpdateView):
    """
    Displays a form to update an existing game.
    Only accessible by the game's author or a superuser.
    """
    model = Game
    form_class = GameForm
    template_name = 'catalog/game_add.html'


class CharacterUpdateView(AuthorOrSuperuserRequiredMixin, UpdateView):
    """
    Displays a form to update an existing character.
    Only accessible by the character's author or a superuser.
    """
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/character_add.html'


class GameDeleteView(AuthorOrSuperuserRequiredMixin, DeleteView):
    """
    Displays a confirmation page to delete an existing game.
    Only accessible by the game's author or a superuser.
    """
    model = Game
    template_name = 'catalog/game_confirm_delete.html'
    success_url = reverse_lazy('catalog:games')


class CharacterDeleteView(AuthorOrSuperuserRequiredMixin, DeleteView):
    """
    Displays a confirmation page to delete an existing character.
    Only accessible by the character's author or a superuser.
    """
    model = Character
    pk_url_kwarg = 'character_slug'
    template_name = 'catalog/character_confirm_delete.html'
    success_url = reverse_lazy('catalog:characters')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CharacterForm(instance=self.object)
        return context
