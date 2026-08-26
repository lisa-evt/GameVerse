from django.db import models
from django.db.models import Count, Q
from django.utils.timezone import now


class UserJournalQuerySet(models.QuerySet):

    def _is_post_q(self):
        return Q(review__isnull=False) & ~Q(review='')

    def visible_to(self, user):
        if not user.is_authenticated:
            return self.filter(self._is_post_q())
        return self.filter(
            Q(user=user) | self._is_post_q()
        )

    def with_comment_count(self):
        return self.annotate(
            comment_count=Count('comments')
        ).order_by('-created_at')

    def posts(self):
        return self.filter(self._is_post_q())
