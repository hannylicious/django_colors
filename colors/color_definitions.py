from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from django.utils.translation import gettext_lazy as _
from typing import Optional, Dict, List, Tuple

if TYPE_CHECKING:
    from .field_type import FieldType


@dataclass(frozen=True, slots=True)
class ColorOption:
    value: str = field(default_factory=str)
    label: str = field(default_factory=str)
    background_css: str = field(default_factory=str)
    text_css: str = field(default_factory=str)
    
    @property
    def instance_choices(self):
        return (self.value, self.label)

    @property
    def extended_choices(self):
        return (self.value, self.label, self.background_css, self.text_css)
    
    def get_by_type(self, field_type: FieldType):
        return getattr(self, field_type.value)


@dataclass(frozen=True, slots=True)
class ColorChoices:
    _value_map: Dict[str, ColorOption] = field(init=False, default_factory=dict)

    def __post_init__(self):
        for color in self.__slots__:
            option = getattr(self, color)
            if isinstance(option, ColorOption):
                self.get_options_dict[option.value] = option

    @property
    def get_options_dict(self):
        return self._value_map

    def get_by_value(self, value: str) -> Optional[ColorOption]:
        return self.get_options_dict.get(value)

    def get_or_raise(self, value: str) -> ColorOption:
        try:
            return self.get_options_dict[value]
        except KeyError:
            raise ValueError(_(f'No color option found with value "{value}"'))

    @property
    def choices(self) -> List[Tuple[str, str]]:
        return [color.instance_choices for color in self.get_options_dict.values()]

    @property
    def extended_choices(self) -> List[Tuple[str, str, str, str]]:
        return [color.extended_choices for color in self.get_options_dict.values()]
    
    def __iter__(self):
        return iter(self.get_options_dict.values())


@dataclass(frozen=True, slots=True)
class BootstrapColorChoices(ColorChoices):
    BLUE: ColorOption = ColorOption('blue', 'Blue', 'bg-primary-200', 'text-primary')
    GREEN: ColorOption = ColorOption('green', 'Green', 'bg-success-200', 'text-success')
    YELLOW: ColorOption = ColorOption('yellow', 'Yellow', 'bg-warning-200', 'text-warning')
    RED: ColorOption = ColorOption('red', 'Red', 'bg-danger-200', 'text-danger')
    PURPLE: ColorOption = ColorOption('purple', 'Purple', 'bg-purple-200', 'text-purple')
    INDIGO: ColorOption = ColorOption('indigo', 'Indigo', 'bg-indigo-200', 'text-indigo')
    PINK: ColorOption = ColorOption('pink', 'Pink', 'bg-pink-200', 'text-pink')
    ORANGE: ColorOption = ColorOption('orange', 'Orange', 'bg-orange-200', 'text-orange')
    TEAL: ColorOption = ColorOption('teal', 'Teal', 'bg-teal-200', 'text-teal')
    CYAN: ColorOption = ColorOption('cyan', 'Cyan', 'bg-cyan-200', 'text-cyan')
    GRAY: ColorOption = ColorOption('gray', 'Gray', 'bg-gray-200', 'text-gray')
