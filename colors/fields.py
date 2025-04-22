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
    value_attribute: FieldType
    default_options: ColorChoices
    description = _("String for use with css (up to %(max_length)s)")

    def __init__(
        self,
        model: Model|None=None,
        queryset: QuerySet|None=None,
        value_attribute: FieldType=FieldType.BACKGROUND,
        default_options: ColorChoices=BootstrapColorChoices,
        *args,
        **kwargs,
    ):
        self.choice_model = model
        self.choice_queryset = queryset
        self.value_attribute = value_attribute
        self.default_options = default_options() #Instance of ColorChoices
        kwargs.setdefault("max_length", 150)

        super().__init__(*args, **kwargs)

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + (
            "choice_model",
            "choice_queryset",
            "default_options",
            "value_attribute",
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.value_attribute:
            kwargs["value_attribute"] = self.value_attribute
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
        """ Returns a list of choices for the field. """
        choices = list(self.default_options.choices) #default choices

        #empty list if no model or queryset is set
        query_model_options = []

        #get model or queryset options just by name (no label required)
        if self.choice_queryset is not None:
            query_model_options = self.choice_queryset.values_list("name", flat=True) 

        elif self.choice_model is not None:
            query_model_options = self.choice_model.objects.all().values_list("name", flat=True)


        #add model or queryset options to choices
        choices.extend([(name, name) for name in query_model_options])

        return choices