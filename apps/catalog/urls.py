from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('games/', views.GamesListView.as_view(), name='games'),
    path('characters/', views.CharactersListView.as_view(), name='characters'),
    path('games/add/', views.GameCreateView.as_view(), name='game_add'),
    path('games/<slug:slug>/', views.GameDetailView.as_view(), name='game_detail'),
    path('characters/add/', views.CharacterCreateView.as_view(), name='character_add'),
    path('characters/<slug:slug>/', views.CharacterDetailView.as_view(), name='character_detail'),
    path('games/<slug:slug>/edit/', views.GameUpdateView.as_view(), name='game_edit'),
    path('characters/<slug:slug>/edit/', views.CharacterUpdateView.as_view(), name='character_edit'),
    path('games/<slug:slug>/delete/', views.GameDeleteView.as_view(), name='game_delete'),
    path('characters/<slug:slug>/delete/', views.CharacterDeleteView.as_view(), name='character_delete'),
]
