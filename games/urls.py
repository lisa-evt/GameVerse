from django.urls import path

from .views import GamesListView, CharactersListView

app_name = 'games'

urlpatterns = [
    path('', GamesListView.as_view(), name='games_library'),
    path('characters/', CharactersListView.as_view(), name='characters_library'),
]