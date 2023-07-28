from decimal import Decimal
from typing import Any

from django import forms

from .models import EbertStrategy, GoodreadsStrategy, MaximusStrategy

GREAT_FILM = "GREAT_FILM"


class EbertStrategyForm(forms.ModelForm[EbertStrategy]):
    rating = forms.ChoiceField(
        choices=(
            (GREAT_FILM, "Great Film"),
            ("4.0", "★★★★"),
            ("3.5", "★★★½"),
            ("3.0", "★★★"),
            ("2.5", "★★½"),
            ("2.0", "★★"),
            ("1.5", "★½"),
            ("1.0", "★"),
            ("0.5", "½"),
            ("0.0", "Zero Stars"),
            (None, "No Star Rating"),
        ),
        initial="4.0",
        label="Rating",
        required=False,
    )

    class Meta:
        model = EbertStrategy
        fields = ["rating"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._set_initial_value(*args, **kwargs)

    def _set_initial_value(self, *args: Any, **kwargs: Any) -> None:
        instance = kwargs.get("instance")
        if instance:
            if instance.great_film:
                self.fields["rating"].initial = GREAT_FILM
            elif instance.stars is None:
                self.fields["rating"].initial = None
            else:
                self.fields["rating"].initial = str(instance.stars)

    def save(self, commit: bool = True) -> EbertStrategy:
        instance = super().save(commit=False)

        rating = self.cleaned_data.get("rating")
        if not rating:
            instance.stars = None
            instance.great_film = False
        elif rating is GREAT_FILM:
            instance.stars = Decimal("4.0")
            instance.great_film = True
        else:
            instance.stars = Decimal(rating)
            instance.great_film = False

        if commit:
            instance.save()
        return instance


class GoodreadsStrategyForm(forms.ModelForm[GoodreadsStrategy]):
    stars = forms.ChoiceField(
        choices=tuple((i, i) for i in range(5, 0, -1)),
        label="Stars",
    )

    class Meta:
        model = GoodreadsStrategy
        fields = ["stars"]


class MaximusStrategyForm(forms.ModelForm[MaximusStrategy]):
    recommended = forms.ChoiceField(
        choices=(
            (True, "Yes"),
            (False, "No"),
        ),
        widget=forms.RadioSelect,
        label="Is it good?",
    )

    class Meta:
        model = MaximusStrategy
        fields = ["recommended"]
