"""Provides custom field types for color selection in Django models."""

from typing import Any

from django.db.models.base import Model
from django.db.models.fields import CharField
from django.forms import ChoiceField
from django.utils.translation import gettext as _

from django_colors import settings as color_settings
from django_colors.color_definitions import ColorChoices
from django_colors.field_type import FieldType
from django_colors.widgets import ColorChoiceWidget


class ColorModelField(CharField):
    """
    Custom field for selecting colors.

    Provide a choice field with color options, supporting both

    """

    choice_model: Model | None
    choice_filters: dict | None
    color_type: FieldType | None
    default_color_choices: type[ColorChoices] | None
    only_use_custom_colors: bool | None
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model | None = None,
        model_filters: dict | None = None,
        color_type: FieldType | None = None,
        default_color_choices: type[ColorChoices] | None = None,
        only_use_custom_colors: bool | None = None,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """
        Initialize the ColorModelField.

        :argument model: Optional model class for custom colors
        :argument model_filters: Optional queryset for custom colors
        :argument color_type: Optional field type (BACKGROUND or TEXT)
        :argument default_color_choices: Optional default color choices class
        :argument only_use_custom_colors: Whether to use only custom colors
        :returns: None
        :raises Exception: If only_use_custom_colors is True but no model or
            queryset is provided
        """
        self.choice_model = model
        self.choice_filters = model_filters
        self.color_type = color_type
        self.default_color_choices = default_color_choices
        self.only_use_custom_colors = only_use_custom_colors
        if (
            not self.choice_model
            and not self.choice_filters
            and self.only_use_custom_colors
        ):
            err_msg = _(
                "You must have a model or model_filters to use custom colors."
            )
            raise Exception(err_msg)
        self.model_name = None
        self.app_name = None
        kwargs.setdefault("max_length", 150)

        super().__init__(*args, **kwargs)

    def get_config_dict(self) -> dict[str, Any]:
        """
        Get the configuration dictionary for this field.

        Returns the default settings or user configured settings in
        settings.py.

        :returns: Dictionary containing the field configuration
        """
        return color_settings.get_config().get(
            self.app_name, color_settings.get_config().get(_("default"))
        )

    def contribute_to_class(
        self, cls: type[Model], name: str, private_only: bool = False
    ) -> None:
        """
        Override to set up additional attributes when adding to a model class.

        We add model_name and app_name to the field instance for later use.

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
            "choice_filters",
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
        if self.choice_filters:
            kwargs["model_filters"] = self.choice_filters
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

    def get_choices(
        self, additional_filters: dict = None, model_priority: bool = False
    ) -> list[tuple[str, str]]:
        """
        Return a list of choices for the field.

        Combine default color choices with custom colors from
        the model or queryset if configured.

        :returns: List of (value, label) tuples for use in choice fields
        """
        default_color_choices = self.field_config.get("default_color_choices")
        color_type = self.field_config.get("color_type")

        # default choices
        choices = list(default_color_choices(color_type).choices)

        if not self.field_config.get("choice_model"):
            return choices

        # get the filters (most narrow scope to least narrow scope)
        filters = additional_filters or self.field_config.get("choice_filters")

        # check for model form priority
        if model_priority:
            filters = {}

        # get the queryset options
        query_model_options = []
        query_model_options = self.choice_model.objects.filter(
            **filters
        ).values_list(color_type.value, "name")

        # add model or queryset options to choices
        if not self.field_config.get("only_use_custom_colors"):
            choices.extend(query_model_options)
            return choices
        if self.field_config.get("only_use_custom_colors"):
            return query_model_options
