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

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter game title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': "Write game's description...",
                'rows': 5
            }),

            'cover_image': forms.FileInput(attrs={
                'class': 'photo-input',
                'accept': 'image/*'
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
