from typing import Any, Dict, List, Optional, Type, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.forms import ModelChoiceField, ModelForm

from supergood_reads.utils.content_type import model_to_content_type_id

_M = TypeVar("_M", bound=Model)


class GenericRelationFormGroup:
    """Instantiate ModelForms for generic relations and associate them with their content_type_id.

    Args:
        form_classes: list of form classes to instantiate.
        selected_form_id: The content_type_id for the model whose form was selected to
          be filled out by the client.
        data: optional request.POST data to handle form submissions.
        instance: pre-existing instance that is being updated.

    """

    def __init__(
        self,
        form_classes: List[Type[ModelForm[Any]]],
        selected_form_id: Optional[int] = None,
        data: Optional[Any] = None,
        instance: Optional[Model] = None,
    ) -> None:
        self.form_classes = form_classes
        self.selected_form_id = selected_form_id
        self.data = data
        self.instance = instance
        self.by_content_type_id = self.instantiate_forms_by_content_type_id()
        self.selected_form = self.get_selected_form()

    def instantiate_forms_by_content_type_id(self) -> Dict[int, ModelForm[Any]]:
        """Organize forms by their content_type_id.

        This is useful in template rendering. A field can select a Model's
        content_type_id (7) and it can be connected to the desired ModelForm
        (EbertStrategyForm).

        Example:
            self.forms = [EbertStrategyForm, GoodreadsStrategyForm, TomatoStrategyForm]
            self.forms_by_content_type_id -> {
                7: EbertStrategyForm(),
                8: GoodreadsStrategyForm(),
                9: TomatoStrategyForm(),
            }
        """
        forms_by_content_type_id = {}

        if self.instance:
            instance_content_type_id = model_to_content_type_id(self.instance)
        else:
            instance_content_type_id = None

        for form_class in self.form_classes:
            form_model = form_class()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = model_to_content_type_id(form_model)

            # Plug in instance or data into selected_form
            if (
                self.instance or self.data
            ) and model_content_type_id == self.selected_form_id:
                if instance_content_type_id and (
                    instance_content_type_id == self.selected_form_id
                ):
                    instance = self.instance
                else:
                    instance = None
                instantiated_form = form_class(
                    self.data, instance=instance, prefix=model_name
                )
            else:
                instantiated_form = form_class(prefix=model_name)

            forms_by_content_type_id[model_content_type_id] = instantiated_form

        return forms_by_content_type_id

    def get_selected_form(self) -> Optional[ModelForm[Any]]:
        """Returns selected Form.

        Example:
            self.selected_form_id = 7
            self.forms_by_content_type_id = {
                7: EbertStrategyForm(),
                8: GoodreadsStrategyForm(),
                9: TomatoStrategyForm(),
            }
            self.selected_form -> EbertStrategyForm()
        """
        if self.selected_form_id:
            return self.by_content_type_id[self.selected_form_id]
        return None


class ContentTypeChoiceField(ModelChoiceField):
    """Choose a ContentType instance from a list of Models."""

    def label_from_instance(self, obj: Model) -> str:
        assert isinstance(obj, ContentType)
        return obj.name

    def __init__(
        self,
        parent_model: type[Model],
        *args: Any,
        models: list[_M] | list[type[_M]] | None = None,
        **kwargs: Any,
    ) -> None:
        queryset = ContentType.objects.none()
        super().__init__(queryset, *args, **kwargs)
        self.parent_model = parent_model
        if models:
            self.set_models(models)

    def set_models(self, models: list[_M] | list[type[_M]]) -> None:
        """Set ContentType queryset based on Models."""
        content_types = ContentType.objects.get_for_models(*models).values()
        self.queryset = ContentType.objects.filter(
            pk__in=[ct.pk for ct in content_types]
        )

    def validate(self, value: Model | None) -> None:
        super().validate(value)
        self._validate_parent_model(value)

    def _validate_parent_model(self, value: Model | None) -> None:
        assert isinstance(value, ContentType)
        if not value or not self.parent_model:
            return

        model_class = value.model_class()
        if not (model_class and issubclass(model_class, self.parent_model)):
            raise ValidationError(
                f"{value.name} is not a valid {self.parent_model.__name__}.",
                code="invalid",
            )
