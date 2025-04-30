from django.db.models.fields import CharField
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms import ChoiceField
from django.utils.translation import gettext as _
from .widgets import ColorChoiceWidget
from .color_definitions import ColorChoices
from colors import settings as color_settings



class ColorModelField(CharField):
    choice_model: Model
    choice_queryset: QuerySet
    color_type: str | None
    default_color_choices: ColorChoices
    only_use_custom_colors: bool
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model | None = None,
        queryset: QuerySet | None = None,
        color_type: str | None = None,
        default_color_choices: ColorChoices | None = None,
        only_use_custom_colors: bool | None = None,
        *args,
        **kwargs,
    ):
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

    def get_config_dict(self) -> dict:
        return color_settings.get_config().get(
            self.app_name, color_settings.get_config().get(_("default"))
        )

    def contribute_to_class(self, cls, name, private_only=False):
        self.model_name = cls.__name__
        self.app_name = cls._meta.app_label
        self.field_config = color_settings.FieldConfig(cls, self, name)
        return super().contribute_to_class(cls, name, private_only)

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + (
            "choice_model",
            "choice_queryset",
            "default_color_choices",
            "color_type",
            "only_use_custom_colors",
        )

    def deconstruct(self):
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

    def formfield(self, **kwargs):
        """Creates a forms.ChoiceField with a custom widget and choices."""

        kwargs["widget"] = ColorChoiceWidget

        return ChoiceField(choices=self.get_choices, **kwargs)

    def get_choices(self):
        """Returns a list of choices for the field."""
        default_color_choices = self.field_config.get("default_color_choices")
        field_type = self.field_config.get("color_type")
        choices = list(default_color_choices(field_type).choices)  # default choices

        # empty list if no model or queryset is set
        query_model_options = []

        # get model or queryset options just by name (no label required)
        if self.choice_queryset is not None:
            query_model_options = self.choice_queryset.values_list(
                field_type.value, "name"
            )
        elif self.choice_model is not None:
            query_model_options = self.choice_model.objects.all().values_list(
                field_type.value, "name"
            )

        # add model or queryset options to choices
        if not self.field_config.get("only_use_custom_colors"):
            choices.extend(query_model_options)
        if self.field_config.get("only_use_custom_colors"):
            choices = query_model_options

        return choices
