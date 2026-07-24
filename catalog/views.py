from django.shortcuts import render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from .models import Game, Character, Quest

GAMES_PER_PAGE = 10
CHARACTERS_PER_PAGE = 20


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