from django import forms

from .models import Character, Game

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = (
            'title',
            'release_year',
            'publisher',
            'metacritic_score',
            'genres',
            'description',
            'cover_image',
            'banner_image',
        )

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Game title',
            }),

            'release_year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Release year',
            }),

            'publisher': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Publisher',
            }),

            'metacritic_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Metacritic',
                'step': '0.1',
            }),

            'genres': forms.SelectMultiple(attrs={
                'class': 'form-select',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Game description...',
            }),

            'cover_image': forms.FileInput(attrs={
                'class': 'photo-input',
                'accept': 'image/*',
            }),
            'banner_image': forms.FileInput(attrs={
                'class': 'banner-input',
                'accept': 'image/*',
            }),
        }


class CharacterForm(forms.ModelForm):
    game = forms.ModelChoiceField(
        queryset=Game.objects.order_by('title'),
        empty_label='Select a game',
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

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
                'placeholder': 'Character name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Character description...',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'photo-input',
                'accept': 'image/*',
            }),
        }


# class CharacterForm(forms.ModelForm):
#     class Meta:
#         model = Character
#         fields = (
#             'name',
#             'game',
#             'description',
#             'photo',
#         )

#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-input',
#                 'placeholder': "Enter character's name"
#             }),
#             'game': forms.Select(attrs={
#                 'class': 'form-select',
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-textarea',
#                 'placeholder': "Write character's description...",
#                 'rows': 5
#             }),
#             'photo': forms.FileInput(attrs={
#                 'class': 'photo-input',
#                 'accept': 'image/*'
#             }),
#         }
