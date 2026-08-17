from .models import UserJournal, Comment, FavoriteQuote, Screenshot
from django import forms
from apps.catalog.models import Character, Quest

from django.forms import inlineformset_factory


class FavoriteQuoteForm(forms.ModelForm):
    class Meta:
        model = FavoriteQuote
        fields = ('quote', 'character')

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        if game is not None:
            self.fields['character'].queryset = Character.objects.filter(game=game)


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshot
        fields = ('screenshot', 'caption')


QuoteFormSet = inlineformset_factory(
    UserJournal,
    FavoriteQuote,
    form=FavoriteQuoteForm,
    extra=1,
    can_delete=True,
)

ScreenshotFormSet = inlineformset_factory(
    UserJournal,
    Screenshot,
    form=ScreenshotForm,
    extra=1,
    can_delete=True,
)


class GameStatusForm(forms.ModelForm):
    """для «+ My List» — только статус"""
    class Meta:
        model = UserJournal
        fields = ['status']


class JournalEntryForm(forms.ModelForm):
    favorite_characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.none(),
        required=False,
    )
    widgets = {
        'favorite_quests': forms.CheckboxSelectMultiple,
    }

    class Meta:
        model = UserJournal
        fields = (
            'status',
            'review',
            'personal_rating',
            'is_on_showcase',
            'favorite_quests',
            'completed_date',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game = self.instance.game
        self.fields['favorite_characters'].queryset = Character.objects.filter(game=game)
        self.fields['favorite_characters'].initial = Character.objects.filter(
            favorited_by_users__user=self.instance.user, game=game,
        )
        self.fields['favorite_quests'].queryset = Quest.objects.filter(game=game)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._sync_favorite_characters(instance)
        return instance

    def _sync_favorite_characters(self, instance):
        selected = set(self.cleaned_data['favorite_characters'])
        existing = FavoriteCharacter.objects.filter(
            user=instance.user, character__game=instance.game,
        ).select_related('character')
        existing_characters = {fc.character for fc in existing}

        to_add = selected - existing_characters
        to_remove = existing_characters - selected

        FavoriteCharacter.objects.bulk_create([
            FavoriteCharacter(user=instance.user, character=character)
            for character in to_add
        ])
        if to_remove:
            FavoriteCharacter.objects.filter(
                user=instance.user, character__in=to_remove,
            ).delete()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)