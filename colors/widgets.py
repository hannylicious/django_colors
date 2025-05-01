"""Widgets for color selection."""

from django import forms


class ColorChoiceWidget(forms.Select):
    """Custom widget for color selection."""

    template_name = "color_select.html"
    option_template_name = "color_select_option.html"
