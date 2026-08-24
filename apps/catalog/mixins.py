from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CharacterForm, GameForm
from .models import Character, Game


class AuthorAssignmentMixin:
    """Assigns the current user as the author before saving the object."""

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class AuthorOrSuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that verifies the current user is either the author of the object
    or a superuser.
    """

    def get_object(self, queryset=None):
        """
        Retrieves the object and caches it on the instance to prevent
        duplicate database queries during the view's lifecycle.
        """
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        target_object = self.get_object()
        return (target_object.added_by == self.request.user) or self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Redirects unauthorized users to the object's detail page instead
        of showing a 403 Forbidden error.
        """
        return redirect(self.get_object().get_absolute_url())
