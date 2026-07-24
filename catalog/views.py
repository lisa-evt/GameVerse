from django.shortcuts import render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from .models import Game, Character

ELEMENTS_PER_PAGE = 10


class GamesListView(ListView):
    model = Game
    paginate_by = ELEMENTS_PER_PAGE
    template_name = 'catalog/games.html'


class CharactersListView(ListView):
    model = Character
    paginate_by = ELEMENTS_PER_PAGE
    template_name = 'catalog/characters.html'

