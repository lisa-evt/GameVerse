from django.urls import path

from .views import GamesListView

app_name = 'games'

urlpatterns = [
    path('', GamesListView.as_view(), name='games_library'),
]
