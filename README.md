# django-colors

[![PyPI version](https://badge.fury.io/py/django-colors.svg)](https://badge.fury.io/py/django-colors)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Django app providing customizable color selection fields for your models with
Bootstrap color integration. Can be used with or without Bootstrap and can be
easily extended to support any CSS framework or custom color palette.

## Overview

Django Colors offers a simple yet powerful way to add color selection
capabilities to your Django models. It provides:

- Custom model fields for color selection
- Pre-defined Bootstrap color choices
- Support for both background and text color CSS classes
- Ability to define your own color palettes
- Ability to define color palettes from any CSS framework
- Custom widget for color selection in forms

The app is designed to be flexible, allowing you to use either the built-in
Bootstrap color options or define your own custom colors through Django models.

## Installation

```bash
pip install django-colors
```

Add 'django_colors' to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    ...
    'django_colors',
    ...
]
```

## Usage

### Basic Usage

Add a color field to your model:

```python
from django.db import models
from django_colors.fields import ColorModelField

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    color = ColorModelField()
```

By default, this will use Bootstrap color choices for background colors.

### Using Text Colors

To use text colors instead of background colors:

```python
from django_colors.field_type import FieldType

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    color = ColorModelField(color_type=FieldType.TEXT)
```

### Custom Color Models

Create a model for custom colors:

```python
from django_colors.models import ColorModel

class MyCustomColor(ColorModel):
    """Custom color definitions for my app."""
    class Meta:
        verbose_name = "Custom Color"
        verbose_name_plural = "Custom Colors"
```

Use your custom colors in a field:

```python
class MyModel(models.Model):
    name = models.CharField(max_length=100)
    color = ColorModelField(model=MyCustomColor)
```

### Global Configuration

You can configure the app globally in your settings.py:

```python
COLORS_APP_CONFIG = {
    'default': {
        'default_color_choices': 'django_colors.color_definitions.BootstrapColorChoices',
        'color_type': 'BACKGROUND',
    },
    'my_app': {
        'default_color_choices': 'myapp.MyCustomColorChoices',
        'color_type': 'TEXT',
    },
    'my_app.MyModel.color_field': {
        'model': 'my_app.MyCustomColor',
        'only_use_custom_colors': True,
    },
}
# You can also import your custom color choices directly

from django_colors.color_definitions import BootstrapColorChoices
COLORS_APP_CONFIG = {
    'default': {
        'default_color_choices': BootstrapColorChoices,
        'color_type': 'BACKGROUND',
    },
    'my_app': {
        'default_color_choices': 'myapp.MyCustomColorChoices',
        'color_type': 'TEXT',
    },
    'my_app.MyModel.color_field': {
        'model': 'my_app.MyCustomColor',
        'only_use_custom_colors': True,
    },
}

```

- *note:* When using `only_use_custom_colors`, you must set a model, as it will
  not use the default color choices.

## Templates

The app includes templates for rendering color selections:

- `color_select.html` - Main template for the color selection widget
- `color_select_option.html` - Template for individual color options

You can override these templates in your project by creating your own versions in
your templates directory.

## API Reference

### ColorOption

A dataclass representing a single color option with the following attributes:

- `value`: Unique identifier for the color
- `label`: Human-readable label
- `background_css`: CSS class for background color
- `text_css`: CSS class for text color

### ColorChoices

Base class for defining a collection of color options with methods to:

- Get choices as a list of tuples for Django choice fields
- Look up color options by value
- Iterate over available color options

### BootstrapColorChoices

Pre-defined color choices based on Bootstrap's color system, including:

- Primary colors (blue: bg-primary, text-primary)
- Success (green: bg-success, text-success)
- Warning (yellow: bg-warning, text-warning)
- Danger (red: bg-danger, text-danger)
- Various other colors (purple, indigo, pink, etc.)

### FieldType

Enum defining the type of color field:

- `BACKGROUND`: For background color CSS classes
- `TEXT`: For text color CSS classes

### ColorModelField

A custom Django field for selecting colors, with options for:

- Using predefined or custom colors
- Specifying field type (background or text)
- Using a custom model or queryset for color options
- String model references (e.g., `"myapp.MyModel"`)
- Flexible choice layout and sorting options

#### Field Parameters

- `model`: Model class or string reference for custom colors
- `model_filters`: Dictionary of filters to apply to the custom model queryset
- `color_type`: FieldType.BACKGROUND or FieldType.TEXT
- `default_color_choices`: Class to use for default color choices
- `only_use_custom_colors`: If True, only show custom colors (no defaults)
- `ordering`: Tuple of field names for ordering custom model choices
- `layout`: Layout for combining default and custom choices ("defaults_first", "custom_first", "mixed")

#### get_choices() Method

The `get_choices()` method provides flexible options for retrieving color choices:

```python
field.get_choices(
    additional_filters=None,  # Extra filters for model queryset
    model_priority=False,     # Ignore filters and return all model options
    include_blank=False,      # Include blank option
    blank_choice="---------", # Custom blank choice text
    ordering=None,            # Override field ordering
    layout=None,              # Override field layout
    sort_by=None,             # Sort by "value" or "label"
)
```

### ColorModel

Abstract base model for custom color definitions with fields for:

- `name`: Color name
- `background_css`: CSS class for background color
- `text_css`: CSS class for text color

### ColorChoiceWidget

Custom form widget for color selection.

### Forms

The `ColorModelField` class will render as a Select field in forms.

#### Model form example

```python
# models.py
from django.db import models
from django_colors.models import ColorModel
from django_colors.fields import ColorModelField

class TestAppColor(ColorModel):
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name}"


class TestThing(models.Model):
    identity = models.CharField(max_length=100)
    background_color = ColorModelField(
        model=TestAppColor,
        # Show only active colors along with default colors
        model_filters={"active": True},
        only_use_custom_colors=False,
        ordering=("name",),  # Order custom colors by name
        layout="defaults_first",  # Default colors first, then custom
        null=True,
        blank=True,
    )
    # Show only default colors
    text_color = ColorModelField()

# forms.py
from django import forms

class TestThingForm(forms.ModelForm):
    class Meta:
        model = TestThing
        fields = ["background_color", "text_color"]
```

#### Standard form example

```python
# models.py
from django.db import models
from django_colors.models import ColorModel
from django_colors.fields import ColorModelField
from django_colors.widgets import ColorChoiceWidget

class TestAppColor(ColorModel):
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name}"


class TestThing(models.Model):
    identity = models.CharField(max_length=100)
    background_color = ColorModelField(
        model=TestAppColor,
        model_filters={"active": True},
        only_use_custom_colors=False,
        null=True,
        blank=True,
    )
    text_color = ColorModelField()

# forms.py
from django import forms

class StandardForm(forms.Form):
    color = forms.ChoiceField(
        required=False,
        choices=TestThing._meta.get_field("background_color").get_choices(),
        widget=ColorChoiceWidget(
            attrs={"class": "form-control", "hx-target": "#something"}
        ),
    )
```

#### Advanced form example

This showcases how to use the `get_choices` method to override the presets in the form:

```python
# models.py
from django.db import models
from django_colors.models import ColorModel
from django_colors.fields import ColorModelField
from django_colors.widgets import ColorChoiceWidget
from functools import partial

class TestAppColor(ColorModel):
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name}"


class TestThing(models.Model):
    identity = models.CharField(max_length=100)
    background_color = ColorModelField(
        model=TestAppColor,
        model_filters={"active": True},
        only_use_custom_colors=False,
        null=True,
        blank=True,
    )
    text_color = ColorModelField()

# forms.py
from django import forms
from functools import partial

class AdvancedForm(forms.Form):
    # Show ALL options including inactive colors
    all_colors = forms.ChoiceField(
        required=False,
        choices=partial(
            TestThing._meta.get_field("background_color").get_choices,
            model_priority=True,  # Ignore model_filters
        ),
        widget=ColorChoiceWidget(
            attrs={"class": "form-control", "hx-target": "#something"}
        ),
    )

    # Custom layout with sorting
    sorted_colors = forms.ChoiceField(
        required=False,
        choices=partial(
            TestThing._meta.get_field("background_color").get_choices,
            layout="custom_first",
            sort_by="label",
            include_blank=True,
            blank_choice="Choose a color...",
        ),
        widget=ColorChoiceWidget(),
    )

    # Only custom colors, sorted by value
    custom_only = forms.ChoiceField(
        required=False,
        choices=partial(
            TestThing._meta.get_field("background_color").get_choices,
            additional_filters={"active": True},
            layout="mixed",
            sort_by="value",
        ),
        widget=ColorChoiceWidget(),
    )
```

#### Using String Model References

You can reference models using strings, which is useful for avoiding circular imports:

```python
class MyModel(models.Model):
    # Reference another app's model
    color = ColorModelField(
        model="otherapp.ColorModel",
        model_filters={"active": True},
    )

    # Reference a model in the same app
    theme_color = ColorModelField(
        model="myapp.ThemeColor",
        only_use_custom_colors=True,
    )
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines

1. Code should be properly linted and formatted according to the ruff settings
in pyproject.toml
2. All tests must pass, and new code must have tests
3. Add documentation for new features
4. Follow type hinting conventions
5. Include docstrings with argument and return type information
6. All contributions must pass pre-commit checks
7. All new contributions should include relevant tests
8. Run ruff linting and formatting checks before submitting your PR

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Run tests: `pytest`
6. Run linting: `ruff check .`
7. Run formatting: `ruff format .`

When submitting a PR, ensure all pre-commit hooks pass successfully. The CI pipeline will automatically check these for you, but it's best to verify locally first.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
