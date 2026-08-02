path(
    'journal/<str:username>/<slug:game_slug>/',
    UserJournalDetailView.as_view(),
    name='journal_entry',
),