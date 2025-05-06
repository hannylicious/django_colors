"""Models for custom color definitions."""

from django.db.models import Model
from django.db.models.fields import CharField


class ColorModel(Model):
    """
    Abstract base model for custom color definitions.

    Provides fields for color name and CSS classes for both background and text
    colors.
    """

    name = CharField(max_length=100)
    background_css = CharField(max_length=200)
    text_css = CharField(max_length=200)

    class Meta:
        """Meta options for the ColorModel."""

        abstract = True
