"""Common definitions for the django_colors app."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.utils.translation import gettext_lazy as _

from django_colors.field_type import FieldType


@dataclass(frozen=True, slots=True)
class ColorOption:
    """
    Color options for color choices.

    Attributes:
        value: Unique identifier for the color option
        label: Human-readable label for the color option
        background_css: CSS class for background color
        text_css: CSS class for text color
    """

    value: str = field(default_factory=str)
    label: str = field(default_factory=str)
    background_css: str = field(default_factory=str)
    text_css: str = field(default_factory=str)

    def instance_choices(
        self, field_type: FieldType = None
    ) -> tuple[str, str]:
        """
        Get a tuple pairing the value of the option to the label.

        :argument field_type: The field type to use for value selection
        :returns: A tuple of (value, label) for use in Django choice fields
        """
        return (getattr(self, field_type.value), self.label)


@dataclass(frozen=True, slots=True)
class ColorChoices:
    """
    Choices for various colors.

    Attributes:
        _value_map: Internal mapping of color values to ColorOption instances
        field_type: The field type to use for value selection
    """

    _value_map: dict[str, ColorOption] = field(
        init=False, default_factory=dict
    )
    field_type: FieldType = field(default=FieldType.BACKGROUND)

    def __post_init__(self) -> None:
        """
        Create dict of ColorOptions using slots to avoid additional iterations.

        :returns: None
        """
        for color in self.__slots__:
            option = getattr(self, color)
            if isinstance(option, ColorOption):
                self.get_options_dict[option.value] = option

    @property
    def get_options_dict(self) -> dict[str, ColorOption]:
        """
        Get the options in a dict.

        :returns: Dictionary mapping color values to ColorOption instances
        """
        return self._value_map

    def get_by_value(self, value: str) -> ColorOption | None:
        """
        Get the ColorOptions from the dict by the value provided.

        :argument value: The color value to look up
        :returns: The ColorOption instance if found, None otherwise
        """
        return self.get_options_dict.get(value)

    def get_or_raise(self, value: str) -> ColorOption:
        """
        Try to access dict using value provided or raise ValueError.

        :argument value: The color value to look up
        :returns: The ColorOption instance
        :raises ValueError: If no color option is found with the provided value
        """
        try:
            return self.get_options_dict[value]
        except KeyError:
            raise KeyError(
                _(f'No color option found with value "{value}".')
            ) from None

    @property
    def choices(self) -> list[tuple[str, str]]:
        """
        Get a list of tuples for the colors from the options dict.

        :returns: A list of (value, label) tuples used in Django choice fields
        """
        return [
            color.instance_choices(self.field_type)
            for color in self.get_options_dict.values()
        ]

    def __iter__(self) -> iter:
        """
        Return an iterator over the color options.

        :returns: Iterator over ColorOption instances
        """
        return iter(self.get_options_dict.values())


@dataclass(frozen=True, slots=True)
class BootstrapColorChoices(ColorChoices):
    """
    Color choices for the Bootstrap framework.

    Provides a set of predefined color options based on Bootstrap CSS classes.
    """

    BLUE: ColorOption = ColorOption(
        "blue", "Blue", "bg-primary", "text-primary"
    )
    GREEN: ColorOption = ColorOption(
        "green", "Green", "bg-success", "text-success"
    )
    YELLOW: ColorOption = ColorOption(
        "yellow", "Yellow", "bg-warning", "text-warning"
    )
    RED: ColorOption = ColorOption("red", "Red", "bg-danger", "text-danger")
    PURPLE: ColorOption = ColorOption(
        "purple", "Purple", "bg-purple", "text-purple"
    )
    INDIGO: ColorOption = ColorOption(
        "indigo", "Indigo", "bg-indigo", "text-indigo"
    )
    PINK: ColorOption = ColorOption("pink", "Pink", "bg-pink", "text-pink")
    ORANGE: ColorOption = ColorOption(
        "orange", "Orange", "bg-orange", "text-orange"
    )
    TEAL: ColorOption = ColorOption("teal", "Teal", "bg-teal", "text-teal")
    CYAN: ColorOption = ColorOption("cyan", "Cyan", "bg-cyan", "text-cyan")
    GRAY: ColorOption = ColorOption("gray", "Gray", "bg-gray", "text-gray")
