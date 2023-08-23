from typing import Any, Dict, List, Optional, Type

from django.db.models import Model
from django.forms import ModelForm

from supergood_reads.utils import ContentTypeUtils


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

    def instantiate_forms_by_content_type_id(self) -> Dict[str, ModelForm[Any]]:
        """ "Organize forms by their content_type_id.

        This is useful in template rendering. A field can select a Model's
        content_type_id (like "7") and it can be connected to the desired ModelForm
        ("EbertStrategyForm").

        Example:
            self.forms = [EbertStrategyForm, GoodreadsStrategyForm, MaximusStrategyForm]
            self.forms_by_content_type_id -> {
                "7": EbertStrategyForm(),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
        """
        forms_by_content_type_id = {}

        if self.instance:
            instance_content_type_id = ContentTypeUtils.get_content_type_id(
                self.instance
            )
        else:
            instance_content_type_id = None

        for form_class in self.form_classes:
            form_model = form_class()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = ContentTypeUtils.get_content_type_id(form_model)

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

            forms_by_content_type_id[str(model_content_type_id)] = instantiated_form

        return forms_by_content_type_id

    def get_selected_form(self) -> Optional[ModelForm[Any]]:
        """Returns selected Form.

        Example:
            self.selected_form_id = 7
            self.forms_by_content_type_id = {
                "7": EbertStrategyForm(),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
            self.selected_form -> EbertStrategyForm()
        """
        if self.selected_form_id:
            return self.by_content_type_id[str(self.selected_form_id)]
        return None
