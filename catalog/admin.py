from django.contrib import admin

from .models import Character, Game, Genre, Quest


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'game',)
    list_filter = ('game',)
    readonly_fields = ('slug',)


class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'realise_year')
    search_fields = ('title', 'publisher',)
    readonly_fields = ('slug',)


class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'game',)
    list_filter = ('game',)


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Genre)
admin.site.register(Quest, QuestAdmin)
