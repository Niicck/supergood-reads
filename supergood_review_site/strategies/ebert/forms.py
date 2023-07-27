from decimal import Decimal
from typing import Any

from django import forms

from .models import EbertStrategy

GREAT_FILM = "GREAT_FILM"


class EbertStrategyForm(forms.ModelForm[EbertStrategy]):
    rating = forms.ChoiceField(
        choices=(
            (None, ""),
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

    def save(self, commit=True):
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
