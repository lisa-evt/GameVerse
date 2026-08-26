from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class AuthorAssignmentMixin:
    """Assigns the current user as the author before saving the object."""

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restricts access to the object's owner.

    Subclasses must set `owner_field` to the FK field name that identifies
    the object's owner (e.g. 'user' for UserJournal, 'added_by' for
    Game/Character). Optionally set `allow_superuser = True` to also grant
    access to superusers.
    """
    owner_field = None
    allow_superuser = False

    def get_object(self, queryset=None):
        """Caches the object to avoid duplicate queries during the request."""
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        obj = self.get_object()
        owner = getattr(obj, self.owner_field)
        is_owner = owner == self.request.user
        return is_owner or (self.allow_superuser and self.request.user.is_superuser)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            # not logged in at all -> redirect to login
            return super().handle_no_permission()
        # logged in, but not the owner -> send them back to the object's page
        return redirect(self.get_object().get_absolute_url())
