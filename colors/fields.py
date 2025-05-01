"""Provides custom field types for color selection in Django models."""

from typing import Any

from django.db.models.base import Model
from django.db.models.fields import CharField
from django.db.models.query import QuerySet
from django.forms import ChoiceField
from django.utils.translation import gettext as _

from colors import settings as color_settings
from colors.color_definitions import ColorChoices
from colors.field_type import FieldType
from colors.widgets import ColorChoiceWidget


class ColorModelField(CharField):
    """
    Custom field for selecting colors.

    Provide a choice field with color options, supporting both
    predefined colors and custom colors from a model or queryset.
    """

    choice_model: Model | None
    choice_queryset: QuerySet | None
    color_type: FieldType | None
    default_color_choices: type[ColorChoices] | None
    only_use_custom_colors: bool | None
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model | None = None,
        queryset: QuerySet | None = None,
        color_type: FieldType | None = None,
        default_color_choices: type[ColorChoices] | None = None,
        only_use_custom_colors: bool | None = None,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """
        Initialize the ColorModelField.

        :argument model: Optional model class for custom colors
        :argument queryset: Optional queryset for custom colors
        :argument color_type: Optional field type (BACKGROUND or TEXT)
        :argument default_color_choices: Optional default color choices class
        :argument only_use_custom_colors: Whether to use only custom colors
        :returns: None
        :raises Exception: If only_use_custom_colors is True but no model or
            queryset is provided
        """
        self.choice_model = model
        self.choice_queryset = queryset
        self.color_type = color_type
        self.default_color_choices = default_color_choices
        self.only_use_custom_colors = only_use_custom_colors
        if (
            not self.choice_model
            and not self.choice_queryset
            and self.only_use_custom_colors
        ):
            raise Exception(
                _("You must have a model or queryset to use custom colors.")
            )
        self.model_name = None
        self.app_name = None
        kwargs.setdefault("max_length", 150)

        super().__init__(*args, **kwargs)

    def get_config_dict(self) -> dict[str, Any]:
        """
        Get the configuration dictionary for this field.

        :returns: Dictionary containing the field configuration
        """
        return color_settings.get_config().get(
            self.app_name, color_settings.get_config().get(_("default"))
        )

    def contribute_to_class(
        self, cls: type[Model], name: str, private_only: bool = False
    ) -> None:
        """
        Set up additional attributes when contributing to a model class.

        :argument cls: The model class the field is being added to
        :argument name: The name of the field
        :argument private_only: Whether the field is private
        :returns: None
        """
        self.model_name = cls.__name__
        self.app_name = cls._meta.app_label
        self.field_config = color_settings.FieldConfig(cls, self, name)
        return super().contribute_to_class(cls, name, private_only)

    @property
    def non_db_attrs(self) -> tuple[str, ...]:
        """
        Get the non-database attributes for this field.

        :returns: Tuple of non-database attribute names
        """
        return super().non_db_attrs + (
            "choice_model",
            "choice_queryset",
            "default_color_choices",
            "color_type",
            "only_use_custom_colors",
        )

    def deconstruct(self) -> tuple[str, str, list[object], dict[str, Any]]:
        """
        Deconstruct the field for migrations.

        :returns: Tuple of (name, path, args, kwargs)
        """
        name, path, args, kwargs = super().deconstruct()
        if self.color_type:
            kwargs["color_type"] = self.color_type
        if self.choice_model:
            kwargs["model"] = self.choice_model
        if self.choice_queryset:
            kwargs["queryset"] = self.choice_queryset
        if self.only_use_custom_colors:
            kwargs["only_use_custom_colors"] = self.only_use_custom_colors
        return name, path, args, kwargs

    def formfield(self, **kwargs: dict) -> ChoiceField:
        """
        Create a forms.ChoiceField with a custom widget and choices.

        :argument kwargs: Additional arguments for the form field
        :returns: ChoiceField instance with appropriate widget and choices
        """
        kwargs["widget"] = ColorChoiceWidget

        return ChoiceField(choices=self.get_choices, **kwargs)

    def get_choices(self) -> list[tuple[str, str]]:
        """
        Return a list of choices for the field.

        Combine default color choices with custom colors from
        the model or queryset if configured.

        :returns: List of (value, label) tuples for use in choice fields
        """
        default_color_choices = self.field_config.get("default_color_choices")
        color_type = self.field_config.get("color_type")
        choices = list(
            default_color_choices(color_type).choices
        )  # default choices

        # empty list if no model or queryset is set
        query_model_options = []

        # get model or queryset options just by name (no label required)
        if self.choice_queryset is not None:
            query_model_options = self.choice_queryset.values_list(
                color_type.value, "name"
            )
        elif self.choice_model is not None:
            query_model_options = self.choice_model.objects.all().values_list(
                color_type.value, "name"
            )

        # add model or queryset options to choices
        if not self.field_config.get("only_use_custom_colors"):
            choices.extend(query_model_options)
        if self.field_config.get("only_use_custom_colors"):
            choices = query_model_options

        return choices
