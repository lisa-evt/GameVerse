from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from catalog.models import Game
from .forms import GameStatusForm
from .models import UserJournal

from django.contrib.auth import get_user_model

User = get_user_model()



class GameStatusQuickView(LoginRequiredMixin, View):
    """Handles `+ My list` button on game_detail page:
    creates / updates status. Does not require any other fields"""

    def post(self, request, game_slug):
        game = get_object_or_404(Game, slug=game_slug)
        personal_status, _ = UserJournal.objects.get_or_create(
            user=request.user, game=game
        )
        form = GameStatusForm(request.POST, instance=personal_status)
        if not form.is_valid():
            messages.error(request, "There was an error processing your request.")
            return redirect(game.get_absolute_url())
        form.save()
        return redirect(game.get_absolute_url())


class UserJournalListView(ListView):
    model = UserJournal
    paginate_by = 5
    template_name = 'journal/profile.html'

    def get_queryset(self):
        User = get_user_model()
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return (
            UserJournal.objects
            .filter(user=self.profile_user)
            .posts()
            .with_comment_count()
        )

class UserJournalDetailView(DetailView):
    model = UserJournal
    template_name = 'journal/journal_entry.html'

    def get_object(self):
        return get_object_or_404(
            UserJournal.objects
            .select_related('user', 'game')
            .prefetch_related(
                'favorite_quests', 'screenshots', 'comments__author',
            )
            .visible_to(self.request.user),
            user__username=self.kwargs['username'],
            game__slug=self.kwargs['game_slug'],
        )

