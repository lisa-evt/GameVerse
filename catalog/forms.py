from django import forms

from .models import Character, Game


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

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = (
            'name',
            'game',
            'description',
            'photo',
        )

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Enter character's name"
            }),

            'game': forms.Select(attrs={
                'class': 'form-select',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': "Write character's description...",
                'rows': 5
            }),

            'photo': forms.FileInput(attrs={
                'class': 'photo-input',
                'accept': 'image/*'
            }),
        }