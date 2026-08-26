from django.urls import path

from . import views

app_name = 'journal'

urlpatterns = [
    path(
        'game/<slug:game_slug>/status/',
        views.GameStatusQuickView.as_view(),
        name='game_status_quick',
    ),
    path(
        '<str:username>/',
        views.UserJournalListView.as_view(),
        name='journal_list',
    ),
    path(
        '<str:username>/<slug:game_slug>/edit/',
        views.UserJournalUpdateView.as_view(),
        name='journal_entry_edit',
    ),
    path(
        '<str:username>/<slug:game_slug>/delete/',
        views.UserJournalDeleteView.as_view(),
        name='journal_entry_delete',
    ),
    path(
        '<str:username>/<slug:game_slug>/comment/',
        views.CommentCreateView.as_view(),
        name='comment_create',
    ),
    path(
        '<str:username>/<slug:game_slug>/',
        views.UserJournalDetailView.as_view(),
        name='journal_entry_detail',
    ),
    path(
        'comment/<int:pk>/delete/',
        views.CommentDeleteView.as_view(),
        name='comment_delete',
    ),
    path(
        'character/<slug:character_slug>/favorite/',
        views.FavoriteCharacterToggleView.as_view(),
        name='favorite_toggle',
    ),
    path(
        'character/<slug:character_slug>/showcase/',
        views.FavoriteCharacterShowcaseToggleView.as_view(),
        name='favorite_showcase_toggle',
    ),
]
