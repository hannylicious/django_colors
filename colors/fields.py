from django.db.models.fields import CharField
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms import ChoiceField
from django.utils.translation import gettext as _
from .widgets import ColorChoiceWidget
from .color_definitions import ColorChoices, BootstrapColorChoices
from .field_type import FieldType


class ColorModelField(CharField):
    choice_model: Model
    choice_queryset: QuerySet
    color_type: FieldType
    default_options: ColorChoices
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model | None = None,
        queryset: QuerySet | None = None,
        color_type: FieldType = FieldType.BACKGROUND,
        default_options: ColorChoices = BootstrapColorChoices,
        *args,
        **kwargs,
    ):
        self.choice_model = model
        self.choice_queryset = queryset
        self.color_type = color_type
        self.default_options = default_options(field_type=self.color_type)
        kwargs.setdefault("max_length", 150)

        super().__init__(*args, **kwargs)

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + (
            "choice_model",
            "choice_queryset",
            "default_options",
            "color_type",
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.color_type:
            kwargs["color_type"] = self.color_type
        if self.choice_model:
            kwargs["model"] = self.choice_model
        if self.choice_queryset:
            kwargs["queryset"] = self.choice_queryset
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """Creates a forms.ChoiceField with a custom widget and choices."""

        kwargs["widget"] = ColorChoiceWidget

        return ChoiceField(choices=self.get_choices, **kwargs)

    def get_choices(self):
        """Returns a list of choices for the field."""
        choices = list(self.default_options.choices)  # default choices

        # empty list if no model or queryset is set
        query_model_options = []

        # get model or queryset options just by name (no label required)
        if self.choice_queryset is not None:
            query_model_options = self.choice_queryset.values_list(
                self.color_type.value, "name"
            )

        elif self.choice_model is not None:
            query_model_options = self.choice_model.objects.all().values_list(
                self.color_type.value, "name"
            )

        # add model or queryset options to choices
        choices.extend(query_model_options)

        return choices

