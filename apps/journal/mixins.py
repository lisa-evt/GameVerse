from django.contrib.auth.mixins import UserPassesTestMixin


class CommentDeleteAllowedMixin(UserPassesTestMixin):
    """Разрешает удаление автору комментария, автору записи журнала или суперюзеру."""

    def test_func(self):
        comment = self.get_object()
        user = self.request.user
        return (
            user == comment.author
            or user == comment.journal_entry.user
            or user.is_superuser
        )
