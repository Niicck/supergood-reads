from django import forms

from .models import GoodreadsStrategy


class GoodreadsStrategyForm(forms.ModelForm[GoodreadsStrategy]):
    stars = forms.ChoiceField(choices=tuple((i + 1, i + 1) for i in range(5)))

    class Meta:
        model = GoodreadsStrategy
        fields = ["stars"]
