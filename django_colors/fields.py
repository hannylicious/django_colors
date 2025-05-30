"""Provides custom field types for color selection in Django models."""

from typing import Any

from django.db.models.base import Model
from django.db.models.fields import CharField
from django.forms import ChoiceField
from django.utils.choices import BlankChoiceIterator
from django.utils.translation import gettext as _

from django_colors import settings as color_settings
from django_colors.color_definitions import ColorChoices
from django_colors.field_type import FieldType
from django_colors.widgets import ColorChoiceWidget

BLANK_CHOICE_DASH = "---------"


def combine_choices(
    layout: str, default_choices: list, queryset_choices: list
) -> list:
    """
    Combine default choices with model options.

    :argument default_choices: List of default color choices
    :argument queryset_choices: List of model color options
    :returns: Combined list of choices
    """
    combined_choices = default_choices + queryset_choices
    if layout == "custom_first":
        combined_choices = queryset_choices + default_choices
    return combined_choices


def sort_choices(
    choices: list,
    sort_by: str | None = None,
) -> list:
    """
    Sort the choices.

    :argument choices: List of color choices
    :returns: Sorted list of choices
    """
    if sort_by == "value":
        # sort by the value (first item in tuple)
        choices.sort(key=lambda x: x[0])
    if sort_by == "label":
        # sort by the label (second item in tuple)
        choices.sort(key=lambda x: x[1])

    return choices


class ColorModelField(CharField):
    """
    Custom field for selecting colors.

    Provide a choice field with color options, supporting both
    default color choices and custom colors from a model.
    """

    choice_model: Model | str | None
    choice_filters: dict | None
    color_type: FieldType | None
    default_color_choices: type[ColorChoices] | None
    only_use_custom_colors: bool | None
    ordering: tuple | None
    layout: str | None
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model | str | None = None,  # Now accepts string references
        model_filters: dict | None = None,
        color_type: FieldType | None = None,
        default_color_choices: type[ColorChoices] | None = None,
        only_use_custom_colors: bool | None = None,
        ordering: tuple | None = None,
        layout: str | None = None,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """
        Initialize the ColorModelField.

        :argument model: Optional model class or string reference for colors
        :argument model_filters: Optional queryset for custom colors
        :argument color_type: Optional field type (BACKGROUND or TEXT)
        :argument default_color_choices: Optional default color choices class
        :argument only_use_custom_colors: Whether to use only custom colors
        :argument ordering: Database ordering for custom model choices
        :argument layout: Default choices placement
            ('start', 'end')
        :returns: None
        :raises Exception: If only_use_custom_colors is True but no model or
            queryset is provided
        """
        self.choice_model = model
        self.choice_filters = model_filters
        self.color_type = color_type
        self.default_color_choices = default_color_choices
        self.only_use_custom_colors = only_use_custom_colors
        self.ordering = ordering
        self.layout = layout

        # Note: We can't validate the model reference here if it's a string
        # because apps might not be loaded yet. The validation will happen
        # in the FieldConfig when the model is actually resolved.
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
            "ordering",
            "layout",
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
        self,
        additional_filters: dict | None = None,
        model_priority: bool = False,
        include_blank: bool = False,
        blank_choice: str = BLANK_CHOICE_DASH,
        ordering: tuple | None = None,
        layout: str | None = None,
        sort_by: str | None = "label",
    ) -> list[tuple[str, str]]:
        """
        Return a list of choices for the field.

        Combine default color choices with custom colors from
        the model or queryset if configured.

        :argument additional_filters: Additional filters for model queryset
        :argument model_priority: Prioritize model choices (ignores filters)
        :argument include_blank: Whether to include a blank choice option
        :argument blank_choice: Blank choice label
        :argument ordering: Database ordering for custom model choices
        :argument layout: How to arrange default vs custom choices
            - "defaults_first": Default choices first, then custom choices
            - "custom_first": Custom choices first, then default choices
            - "mixed": All choices combined and sorted together
        :argument sort_by: Sort key ("value" or "label")
        :returns: List of (value, label) tuples for use in choice fields
        """
        ordering, layout = self._resolve_choice_parameters(ordering, layout)
        self._validate_parameters(layout, sort_by)

        # Handle predefined choices early return
        if self.choices is not None:
            return self._handle_predefined_choices(include_blank, blank_choice)

        # Use the resolved default_color_choices from field_config
        default_color_choices = self.field_config.default_color_choices
        color_type = self.field_config.get("color_type")

        # default choices
        default_choices = list(default_color_choices(color_type).choices)

        # Use the resolved choice_model
        resolved_choice_model = self.field_config.choice_model
        if not resolved_choice_model:
            # return the default choices if no model is set
            final_choices = default_choices
        else:
            # get the queryset, filter/sort/etc.
            # get the filters (most narrow scope to least narrow scope)
            filters = additional_filters or self.field_config.get(
                "choice_filters"
            )

            # check for model form priority and return all options if set
            if model_priority:
                filters = {}

            # get the queryset options using the resolved model
            queryset_choices = list(
                resolved_choice_model.objects.filter(**filters)
                .distinct()
                .order_by(*ordering)
                .values_list(color_type.value, "name")
            )
            if sort_by and layout != "mixed":
                # Sort the two lists we have
                # We sort these here in case they want things sorted, but
                # seperated so the combine_choices will keep the options
                # in their places, but sorted as expected.
                default_choices = sort_choices(default_choices, sort_by)
                queryset_choices = sort_choices(queryset_choices, sort_by)

            if self.field_config.get("only_use_custom_colors"):
                final_choices = queryset_choices
            else:
                final_choices = combine_choices(
                    layout,
                    default_choices,
                    queryset_choices,
                )
        if sort_by and layout == "mixed":
            # Mixed list of choices, sort the entire list
            final_choices = sort_choices(final_choices, sort_by)
        if include_blank:
            final_choices.insert(0, ("", blank_choice))
        return final_choices

    def _resolve_choice_parameters(
        self, ordering: tuple | None, layout: str | None
    ) -> tuple:
        """Resolve ordering and layout with field defaults."""
        resolved_ordering = (
            ordering if ordering is not None else (self.ordering or ())
        )
        resolved_layout = (
            layout if layout is not None else (self.layout or "defaults_first")
        )
        return resolved_ordering, resolved_layout

    def _validate_parameters(self, layout: str, sort_by: str | None) -> None:
        """Validate layout and sort_by parameters."""
        if layout not in ("defaults_first", "custom_first", "mixed"):
            raise ValueError(
                f"layout must be 'defaults_first', 'custom_first', or 'mixed',"
                f" got '{layout}'"
            )
        if sort_by not in ("value", "label", None):
            raise ValueError(
                f"sort_by must be 'label', 'value', or not set, "
                f"got '{sort_by}'"
            )

    def _handle_predefined_choices(
        self, include_blank: bool, blank_choice: str
    ) -> list[tuple[str, str]] | BlankChoiceIterator:
        """Handle the case where self.choices is already defined."""
        if include_blank:
            return BlankChoiceIterator(self.choices, blank_choice)
        return self.choices
