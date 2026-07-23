from django.shortcuts import render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from .models import Game

GAMES_PER_PAGE = 12


class GamesListView(ListView):
    model = Game
    paginate_by = GAMES_PER_PAGE
    template_name = 'games/games_library.html'
    context_object_name = 'games_library'

