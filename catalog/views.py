from django.shortcuts import render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Game, Character, Quest
from .forms import GameForm, CharacterForm
from django.shortcuts import redirect
from django.urls import reverse


GAMES_PER_PAGE = 10
CHARACTERS_PER_PAGE = 20


class IsAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.get_object().added_by == self.request.user

    def handle_no_permission(self):
        return redirect(self.get_object().get_absolute_url())


class GamesListView(ListView):
    model = Game
    paginate_by = GAMES_PER_PAGE
    template_name = 'catalog/games.html'


class CharactersListView(ListView):
    model = Character
    paginate_by = CHARACTERS_PER_PAGE
    template_name = 'catalog/characters.html'


class GameDetailView(DetailView):
    model = Game
    template_name = 'catalog/game_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = self.object.characters.all()
        context['quests'] = self.object.quests.all()
        return context


class CharacterDetailView(DetailView):
    model = Character
    template_name = 'catalog/character_detail.html'


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    template_name = 'catalog/add_game.html'

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:game_detail', args=(self.object.slug,))


class CharacterCreateView(CreateView):
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/add_character.html'

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:character_detail', args=(self.object.slug,))


class GameUpdateView(IsAuthorMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'catalog/add_game.html'

    def get_success_url(self):
        return reverse('catalog:game_detail', args=(self.object.slug,))


class CharacterUpdateView(IsAuthorMixin, UpdateView):
    model = Character
    form_class = CharacterForm
    template_name = 'catalog/add_character.html'

    def get_success_url(self):
        return reverse('catalog:character_detail', args=(self.object.slug,))


class GameDeleteView(IsAuthorMixin, DeleteView):
    model = Game
    template_name = 'catalog/game_confirm_delete.html'

    def get_success_url(self):
        return reverse('catalog:games')


class CharacterDeleteView(IsAuthorMixin, DeleteView):
    model = Character
    template_name = 'catalog/character_confirm_delete.html'

    def get_success_url(self):
        return reverse('catalog:characters')
