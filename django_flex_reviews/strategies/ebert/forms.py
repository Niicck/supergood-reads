from decimal import Decimal
from typing import Any, Dict, Optional

from django import forms

from .models import EbertStrategy

GREAT_FILM = "GREAT_FILM"


class EbertStrategyForm(forms.ModelForm[EbertStrategy]):
    rating = forms.ChoiceField(
        choices=(
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
            (GREAT_FILM, "Great Film"),
        )
    )

    class Meta:
        model = EbertStrategy

    def clean(self) -> Optional[Dict[str, Any]]:
        """Convert rating choice into EbertStrategy model fields."""
        final_cleaned_data: Dict[str, Any] = {
            "stars": None,
            "great_film": False,
        }
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        rating = cleaned_data.get("rating")

        if rating is None:
            pass
        elif rating is GREAT_FILM:
            final_cleaned_data["stars"] = Decimal(4)
            final_cleaned_data["great_film"] = True
        else:
            final_cleaned_data["stars"] = Decimal(rating)

        return final_cleaned_data
