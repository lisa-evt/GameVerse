from django.urls import path

from .views import GamesListView, CharactersListView, GameDetailView, CharacterDetailView

app_name = 'catalog'

urlpatterns = [
    path('games/', GamesListView.as_view(), name='games'),
    path('characters/', CharactersListView.as_view(), name='characters'),
    path('games/<slug:slug>/', GameDetailView.as_view(), name='game_detail'),
    path('characters/<slug:slug>/', CharacterDetailView.as_view(), name='character_detail'),
]
