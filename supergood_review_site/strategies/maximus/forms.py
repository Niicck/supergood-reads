from django import forms

from .models import MaximusStrategy


class MaximusStrategyForm(forms.ModelForm[MaximusStrategy]):
    recommended = forms.ChoiceField(
        choices=(
            (True, "Yes"),
            (False, "No"),
            (None, "Meh"),
        ),
        widget=forms.RadioSelect,
        label="Is it good?",
        initial=True,
    )

    class Meta:
        model = MaximusStrategy
        fields = ["recommended"]
