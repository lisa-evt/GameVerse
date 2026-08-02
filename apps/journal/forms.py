class GameStatusForm(forms.ModelForm):
    """для «+ My List» — только статус"""
    class Meta:
        model = UserExperience
        fields = ['status']


class UserExperienceForm(forms.ModelForm):
    """для полноценной записи/поста"""
    class Meta:
        model = UserExperience
        fields = ['status', 'review', 'rating', 'showcase']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['review'].required = True