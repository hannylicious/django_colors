"""Pytest setup for color tests."""

import pytest
from django.db import models

from django_colors.color_definitions import (
    BootstrapColorChoices,
    ColorChoices,
    ColorOption,
)
from django_colors.field_type import FieldType
from django_colors.models import ColorModel


@pytest.fixture
def color_option() -> ColorOption:
    """
    Fixture for creating a ColorOption instance.

    :return: A ColorOption instance
    """
    return ColorOption(
        value="red",
        label="Red",
        background_css="bg-red",
        text_css="text-red",
    )


@pytest.fixture
def color_choice() -> ColorChoices:
    """
    Fixture for creating a ColorChoices instance.

    :return: A ColorChoices instance
    """
    return ColorChoices(
        field_type=FieldType.BACKGROUND,
    )


@pytest.fixture
def bootstrap_color_choice() -> BootstrapColorChoices:
    """
    Fixture for creating a BootstrapColorChoices instance.

    :return: A BootstrapColorChoices instance
    """
    return BootstrapColorChoices(
        field_type=FieldType.BACKGROUND,
    )


@pytest.fixture
def mock_model_class() -> type:
    """
    Create a mock model class for testing.

    :return: A Django model class
    """

    class MockModel(models.Model):
        """Mock model for testing."""

        name = models.CharField(max_length=100)
        background_css = models.CharField(max_length=100)
        text_css = models.CharField(max_length=100)

        class Meta:
            """Meta class for testing."""

            app_label = "test_app"

        def __str__(self) -> str:
            """Return string representation of the model."""
            return self.name

    return MockModel


@pytest.fixture
def concrete_color_model() -> type:
    """
    Create a concrete implementation of ColorModel for testing.

    :return: A concrete ColorModel subclass
    """

    class ConcreteColorModel(ColorModel):
        """Concrete implementation of ColorModel for testing."""

        class Meta:
            """Meta class for testing."""

            app_label = "test_app"

    return ConcreteColorModel
