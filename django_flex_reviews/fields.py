from typing import Any

from django import forms


class VueChoiceField(forms.ChoiceField):
    """Transform values before clean() so that they pass initial validation.

    When form values are bound to hidden inputs in vue components, they are always
    coerced to strings. This will cause boolean or string ChoiceField validation to fail
    even before reaching the clean_<fieldname> step.

    We must transform those values to their appropriate type before the
    ChoiceField.validate() and clean() steps.

    That operation takes place in to_python().
    """

    def transform(self, value: Any) -> Any:
        return value

    def to_python(self, value: Any) -> Any:
        return self.transform(value)


class BoolVueChoiceField(VueChoiceField):
    """Transform string value to boolean."""

    def transform(self, value: Any) -> Any:
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value == "true":
                return True
            elif value == "false":
                return False
            else:
                return None
