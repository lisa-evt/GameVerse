from django.contrib import admin

from .models import (Comment, FavoriteCharacter, FavoriteQuote, Screenshot,
                     UserJournal)


class UserJournalAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status',)
    search_fields = ('game__title',)
    list_filter = ('status',)


admin.site.register(UserJournal, UserJournalAdmin)
admin.site.register(Comment)
admin.site.register(FavoriteCharacter)
admin.site.register(FavoriteQuote)
admin.site.register(Screenshot)
