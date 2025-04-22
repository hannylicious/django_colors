from django.db.models.fields import CharField
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms import ChoiceField
from django.db.models.functions import Lower

from .widgets import ColorChoiceWidget
from .color_definitions import ColorChoices, BootstrapColorChoices


class ColorModelField(CharField):
    choice_model: Model
    choice_queryset: QuerySet
    default_options: ColorChoices

    def __init__(
        self,
        model=None,
        queryset=None,
        default_options=BootstrapColorChoices,
        *args,
        **kwargs,
    ):
        self.choice_model = model
        self.choice_queryset = queryset
        self.default_options = default_options
        kwargs.setdefault("max_length", 32)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        # modified deconstruct method to properly add args (model or queryset) in migration field definition.
        name, path, args, kwargs = super().deconstruct()
        if self.choice_model:
            kwargs["model"] = self.choice_model
        if self.choice_queryset:
            kwargs["queryset"] = self.choice_queryset

        kwargs["default_options"] = self.default_options

        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """Creates a forms.ChoiceField with a custom widget and choices."""

        choices = self.default_options.choices_list()  # default colors

        if self.choice_queryset is not None:
            choices.extend(
                list(
                    self.choice_queryset.values_list(
                        Lower("name"), "name", "bg_css_class", "text_css_class"
                    )
                )
            )

        elif self.choice_model is not None:
            choices.extend(
                list(
                    self.choice_model.objects.all().values_list(
                        Lower("name"), "name", "bg_css_class", "text_css_class"
                    )
                )
            )

        kwargs["widget"] = ColorChoiceWidget(choices=choices)

        return ChoiceField(choices=choices, **kwargs)
