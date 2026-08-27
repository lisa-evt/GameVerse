from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from apps.catalog.mixins import OwnerRequiredMixin
from apps.catalog.models import Character, Game

from .forms import (CommentForm, GameStatusForm, JournalEntryForm,
                    QuoteFormSet, ScreenshotFormSet)
from .models import Comment, FavoriteCharacter, UserJournal

User = get_user_model()
JOURNAL_ENTRIES_PER_PAGE = 5


class JournalEntryContextMixin:

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
        context['game'] = entry.game
        context['favorite_characters'] = FavoriteCharacter.objects.filter(
            user=entry.user, character__game=entry.game,
        ).select_related('character')
        context['form'] = CommentForm()
        return context


class JournalEntryFormsetMixin:

    model = UserJournal
    form_class = JournalEntryForm
    template_name = 'journal/journal_entry_form.html'

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs['game_slug'])

    def assign_new_instance_defaults(self, form):
        """Hook for new object default"""
        pass

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.assign_new_instance_defaults(form)

        screenshot_formset = ScreenshotFormSet(
            request.POST,
            request.FILES,
            instance=self.object,
        )
        quote_formset = QuoteFormSet(
            request.POST,
            instance=self.object,
            form_kwargs={'game': self.game},
        )

        form_valid = form.is_valid()
        screenshot_formset_valid = screenshot_formset.is_valid()
        quote_formset_valid = quote_formset.is_valid()

        if form_valid and screenshot_formset_valid and quote_formset_valid:
            with transaction.atomic():
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        context.setdefault(
            'screenshot_formset',
            ScreenshotFormSet(instance=self.object),
        )
        context.setdefault(
            'quote_formset',
            QuoteFormSet(instance=self.object,
                         form_kwargs={'game': self.game}),
        )
        return context


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
        self.profile_user = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return (
            UserJournal.objects
            .filter(user=self.profile_user)
            .posts()
            .with_comment_count()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user

        return context


class UserJournalCreateView(
    LoginRequiredMixin, JournalEntryFormsetMixin, CreateView
):

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def assign_new_instance_defaults(self, form):
        form.instance.user = self.request.user
        form.instance.game = self.game

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['game'] = self.game
        kwargs['user'] = self.request.user
        return kwargs


class UserJournalUpdateView(
    OwnerRequiredMixin, JournalEntryFormsetMixin, UpdateView
):

    owner_field = 'user'

    def get_object(self, queryset=None):
        return get_object_or_404(
            UserJournal,
            user__username=self.kwargs['username'],
            game__slug=self.kwargs['game_slug'],
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class UserJournalDetailView(JournalEntryContextMixin, DetailView):
    model = UserJournal

    def get_object(self, queryset=None):
        return self.get_journal_entry()


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


class CommentCreateView(
    LoginRequiredMixin, JournalEntryContextMixin, CreateView
):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.journal_entry = self.get_journal_entry()
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(OwnerRequiredMixin, DeleteView):
    model = Comment
    template_name = 'journal/comment_confirm_delete.html'

    def test_func(self):
        comment = self.get_object()
        user = self.request.user
        return (
            user == comment.author
            or user == comment.journal_entry.user
            or user.is_superuser
        )

    def get_queryset(self):
        return Comment.objects.select_related(
            'author', 'journal_entry__user', 'journal_entry__game',
        )

    def get_object(self, queryset=None):
        if not hasattr(self, '_comment'):
            self._comment = super().get_object(queryset)
        return self._comment

    def get_success_url(self):
        return self.object.journal_entry.get_absolute_url()


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
    def post(self, request, character_slug):
        favorite = get_object_or_404(
            FavoriteCharacter,
            user=request.user,
            character__slug=character_slug,
        )
        favorite.is_on_showcase = not favorite.is_on_showcase
        favorite.save(update_fields=['is_on_showcase'])
        return redirect('journal:journal_list', username=request.user.username)
