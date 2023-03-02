from django import forms

from .models import GoodreadsStrategy


class GoodreadsStrategyForm(forms.ModelForm[GoodreadsStrategy]):
    stars = forms.ChoiceField(
        choices=tuple((i, i) for i in range(5, 0, -1)),
        label="How many stars would you give it?",
    )

    class Meta:
        model = GoodreadsStrategy
        fields = ["stars"]
