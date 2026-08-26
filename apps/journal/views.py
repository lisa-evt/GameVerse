from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from apps.catalog.models import Character, Game
from apps.catalog.mixins import OwnerRequiredMixin

from .forms import (CommentForm, GameStatusForm, JournalEntryForm,
                    QuoteFormSet, ScreenshotFormSet)
from .mixins import CommentDeleteAllowedMixin
from .models import Comment, FavoriteCharacter, UserJournal

User = get_user_model()
JOURNAL_ENTRIES_PER_PAGE = 5


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
            messages.error(request, "Error occured while processing request.")
            return redirect(game.get_absolute_url())
        form.save()
        return redirect(game.get_absolute_url())


class UserJournalListView(ListView):
    model = UserJournal
    paginate_by = JOURNAL_ENTRIES_PER_PAGE
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


class UserJournalCreateView(LoginRequiredMixin, CreateView):
    model = UserJournal
    form_class = JournalEntryForm
    template_name = 'journal/journal_entry_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = get_object_or_404(
            Game,
            slug=self.kwargs['game_slug'],
        )
        context['game'] = game
        context.setdefault(
            'screenshot_formset',
            ScreenshotFormSet(),
        )
        context.setdefault(
            'quote_formset',
            QuoteFormSet(
                form_kwargs={'game': game},
            ),
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['game'] = get_object_or_404(
            Game,
            slug=self.kwargs['game_slug'],
        )
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        game = get_object_or_404(
            Game,
            slug=self.kwargs['game_slug'],
        )
        screenshot_formset = ScreenshotFormSet(
            request.POST,
            request.FILES,
        )
        quote_formset = QuoteFormSet(
            request.POST,
            form_kwargs={'game': game},
        )
        form.instance.user = request.user
        form.instance.game = game
        if (
            form.is_valid()
            and screenshot_formset.is_valid()
            and quote_formset.is_valid()
        ):
            self.object = form.save()
            screenshot_formset.instance = self.object
            screenshot_formset.save()
            quote_formset.instance = self.object
            quote_formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(
            self.get_context_data(
                form=form,
                screenshot_formset=screenshot_formset,
                quote_formset=quote_formset,
            )
        )

    def get_success_url(self):
        return reverse('journal:journal_entry_detail', kwargs={
            'username': self.object.user.username,
            'game_slug': self.object.game.slug,
        })


class UserJournalUpdateView(OwnerRequiredMixin, UpdateView):
    model = UserJournal
    form_class = JournalEntryForm
    template_name = 'journal/journal_entry_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            UserJournal,
            user__username=self.kwargs['username'],
            game__slug=self.kwargs['game_slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.object.game
        context.setdefault(
            'screenshot_formset',
            ScreenshotFormSet(instance=self.object),
        )
        context.setdefault(
            'quote_formset',
            QuoteFormSet(
                instance=self.object,
                form_kwargs={'game': self.object.game},
            ),
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        screenshot_formset = ScreenshotFormSet(
            request.POST, request.FILES, instance=self.object,
        )
        quote_formset = QuoteFormSet(
            request.POST,
            instance=self.object,
            form_kwargs={'game': self.object.game},
        )

        if form.is_valid() and screenshot_formset.is_valid() and quote_formset.is_valid():
            self.object = form.save()
            screenshot_formset.instance = self.object
            screenshot_formset.save()
            quote_formset.instance = self.object
            quote_formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(
            form=form,
            screenshot_formset=screenshot_formset,
            quote_formset=quote_formset,
        ))

    def get_success_url(self):
        return reverse('journal:journal_entry_detail', kwargs={
            'username': self.object.user.username,
            'game_slug': self.object.game.slug,
        })


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['game'] = self.object.game
        context['favorite_characters'] = FavoriteCharacter.objects.filter(
            user=self.object.user, character__game=self.object.game,
        ).select_related('character')
        return context


class UserJournalDeleteView(OwnerRequiredMixin, DeleteView):
    model = UserJournal
    owner_field = 'user'
    template_name = 'journal/journal_entry_confirm_delete.html'

    def get_object(self, queryset=None):
        if not hasattr(self, '_journal_entry'):
            self._journal_entry = get_object_or_404(
                UserJournal.objects.select_related('user', 'game'),
                user__username=self.kwargs['username'],
                game__slug=self.kwargs['game_slug'],
            )
        return self._journal_entry

    def get_success_url(self):
        return reverse('journal:journal_list', kwargs={
            'username': self.object.user.username,
        })


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'journal/journal_entry.html'

    def get_journal_entry(self):
        if not hasattr(self, '_journal_entry'):
            self._journal_entry = get_object_or_404(
                UserJournal.objects
                .select_related('user', 'game')
                .prefetch_related(
                    'favorite_quests', 'screenshots', 'comments__author',
                )
                .visible_to(self.request.user),
                user__username=self.kwargs['username'],
                game__slug=self.kwargs['game_slug'],
            )
        return self._journal_entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.get_journal_entry()
        context['object'] = entry
        context['favorite_characters'] = FavoriteCharacter.objects.filter(
            user=entry.user, character__game=entry.game,
        ).select_related('character')
        return context

    def form_valid(self, form):
        form.instance.journal_entry = self.get_journal_entry()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        entry = self.get_journal_entry()
        return reverse('journal:journal_entry', kwargs={
            'username': entry.user.username,
            'game_slug': entry.game.slug,
        })


class CommentDeleteView(LoginRequiredMixin, CommentDeleteAllowedMixin, DeleteView):
    model = Comment
    template_name = 'journal/comment_confirm_delete.html'

    def get_queryset(self):
        return Comment.objects.select_related(
            'author', 'journal_entry__user', 'journal_entry__game',
        )

    def get_object(self, queryset=None):
        if not hasattr(self, '_comment'):
            self._comment = super().get_object(queryset)
        return self._comment

    def get_success_url(self):
        entry = self.object.journal_entry
        return reverse('journal:journal_entry', kwargs={
            'username': entry.user.username,
            'game_slug': entry.game.slug,
        })


class FavoriteCharacterToggleView(LoginRequiredMixin, View):
    """Toggles a character in/out of the user's favorites list."""

    def post(self, request, character_slug):
        character = get_object_or_404(Character, slug=character_slug)
        favorite, created = FavoriteCharacter.objects.get_or_create(
            user=request.user, character=character,
        )
        if not created:
            favorite.delete()
        return redirect(character.get_absolute_url())


class FavoriteCharacterShowcaseToggleView(LoginRequiredMixin, View):
    """Toggles whether an already-favorited character is highlighted
    on the user's profile showcase."""

    def post(self, request, character_slug):
        favorite = get_object_or_404(
            FavoriteCharacter,
            user=request.user,
            character__slug=character_slug,
        )
        favorite.is_on_showcase = not favorite.is_on_showcase
        favorite.save(update_fields=['is_on_showcase'])
        return redirect('users:profile', username=request.user.username)
