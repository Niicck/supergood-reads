from typing import Any

from django.forms import BoundField, Field, Form, ModelForm


def get_initial_field_value(form: Form | ModelForm[Any], field_name: str) -> Any:
    """Get the initial value of a form field.

    Normally, the initial values of a form field are set during django template
    rendering. But there are some situations where we want to manually access the
    value of a form field (for example: when assigning initial values to custom vue
    form components).

    Returns:
        If form is pre-populated with data, then use the data that was provided.
        Else, if form is unbound, use the "initial" kwarg value, if it was provided.
    """
    if form.is_bound:
        bound_field: BoundField = form[field_name]
        bound_value = bound_field.value()
        return bound_value
    else:
        form_field: Field = form.fields[field_name]
        initial_value = form.get_initial_for_field(form_field, field_name)
        return initial_value
