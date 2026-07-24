from django.urls import path

from .views import GamesListView, CharactersListView

app_name = 'catalog'

urlpatterns = [
    path('games/', GamesListView.as_view(), name='games'),
    path('characters/', CharactersListView.as_view(), name='characters'),
]