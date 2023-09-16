from decimal import Decimal
from typing import Any

from django import forms

from supergood_reads.models import (
    EbertStrategy,
    GoodreadsStrategy,
    ImdbStrategy,
    LetterboxdStrategy,
    ThumbsStrategy,
    TomatoStrategy,
)

GOAT = "GOAT"


class EbertStrategyForm(forms.ModelForm[EbertStrategy]):
    rating = forms.ChoiceField(
        choices=(
            (GOAT, "GOAT"),
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
            if instance.goat:
                self.fields["rating"].initial = GOAT
            elif instance.stars is None:
                self.fields["rating"].initial = None
            else:
                self.fields["rating"].initial = str(instance.stars)

    def save(self, commit: bool = True) -> EbertStrategy:
        instance = super().save(commit=False)

        rating = self.cleaned_data.get("rating")
        if not rating:
            instance.stars = None
            instance.goat = False
        elif rating == GOAT:
            instance.stars = Decimal("4.0")
            instance.goat = True
        else:
            instance.stars = Decimal(rating)
            instance.goat = False

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


class LetterboxdStrategyForm(forms.ModelForm[EbertStrategy]):
    stars = forms.ChoiceField(
        choices=(
            ("5.0", "★★★★★"),
            ("4.5", "★★★★½"),
            ("4.0", "★★★★"),
            ("3.5", "★★★½"),
            ("3.0", "★★★"),
            ("2.5", "★★½"),
            ("2.0", "★★"),
            ("1.5", "★½"),
            ("1.0", "★"),
            ("0.5", "½"),
        ),
        initial="5.0",
        label="Stars",
        required=True,
    )

    class Meta:
        model = LetterboxdStrategy
        fields = ["stars"]


class ImdbStrategyForm(forms.ModelForm[ImdbStrategy]):
    score = forms.ChoiceField(
        choices=tuple((i, i) for i in range(10, 1, -1)),
        label="Score",
    )

    class Meta:
        model = ImdbStrategy
        fields = ["score"]


class ThumbsStrategyForm(forms.ModelForm[ThumbsStrategy]):
    recommended = forms.ChoiceField(
        choices=(
            (True, "👍"),
            (False, "👎"),
        ),
        widget=forms.RadioSelect,
        label="Is it good?",
    )

    class Meta:
        model = ThumbsStrategy
        fields = ["recommended"]


class TomatoStrategyForm(forms.ModelForm[TomatoStrategy]):
    fresh = forms.ChoiceField(
        choices=(
            (True, "Yes 🍅"),
            (False, "No 🤮"),
        ),
        widget=forms.RadioSelect,
        label="Is it good?",
    )

    class Meta:
        model = TomatoStrategy
        fields = ["fresh"]
