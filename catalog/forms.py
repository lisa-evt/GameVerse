from django import forms

from .models import Character, Game


class CharacterForm(forms.ModelForm):

    class Meta:
        model = Character
        fields = ('name', 'description', 'photo', 'game')


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = (
            'title',
            'description',
            'release_year',
            'publisher',
            'cover_image',
            'banner_image',
            'genres',
        )
