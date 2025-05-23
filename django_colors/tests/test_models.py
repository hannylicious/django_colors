"""Tests for the models module."""

import pytest
from django.db import models
from django.db.models.fields import CharField

from django_colors.models import ColorModel


class TestColorModel:
    """Test the ColorModel class."""

    def test_is_abstract_model(self) -> None:
        """
        Test that ColorModel is an abstract model.

        :return: None
        """
        assert issubclass(ColorModel, models.Model)
        assert ColorModel._meta.abstract is True

    def test_has_name_field(self) -> None:
        """
        Test that ColorModel has a name field.

        :return: None
        """
        field = ColorModel._meta.get_field("name")
        assert isinstance(field, CharField)
        assert field.max_length == 100

    def test_has_background_css_field(self) -> None:
        """
        Test that ColorModel has a background_css field.

        :return: None
        """
        field = ColorModel._meta.get_field("background_css")
        assert isinstance(field, CharField)
        assert field.max_length == 200

    def test_has_text_css_field(self) -> None:
        """
        Test that ColorModel has a text_css field.

        :return: None
        """
        field = ColorModel._meta.get_field("text_css")
        assert isinstance(field, CharField)
        assert field.max_length == 200

    def test_field_order(self) -> None:
        """
        Test the order of fields in the model.

        :return: None
        """
        fields = [field.name for field in ColorModel._meta.fields]
        # Abstract models, the id field might not be included in _meta.fields
        # Check that the other fields are in the expected order
        assert fields == ["name", "background_css", "text_css"]

    def test_id_field_in_color_model(
        self, color_model: pytest.fixture
    ) -> None:
        """
        Test that a concrete subclass has an id field.

        :param color_model: Fixture that provides a concrete
            ColorModel subclass
        :return: None
        """
        fields = [field.name for field in color_model._meta.fields]
        assert "id" in fields
        # Check full order
        assert fields == ["id", "name", "background_css", "text_css"]

    def test_meta_options(self) -> None:
        """
        Test the Meta options of the model.

        :return: None
        """
        assert ColorModel._meta.abstract is True
        assert (
            ColorModel._meta.app_label == "django_colors"
        )  # From the test settings

    def test_concrete_subclass_creation(
        self, color_model: pytest.fixture
    ) -> None:
        """
        Test creating a concrete subclass of ColorModel.

        :param color_model: Fixture that provides a concrete
            ColorModel subclass
        :return: None
        """
        # Should inherit all fields
        assert hasattr(color_model, "name")
        assert hasattr(color_model, "background_css")
        assert hasattr(color_model, "text_css")

        # Should not be abstract
        assert color_model._meta.abstract is False

        # Fields should maintain their properties
        assert color_model._meta.get_field("name").max_length == 100
        assert color_model._meta.get_field("background_css").max_length == 200
        assert color_model._meta.get_field("text_css").max_length == 200

    @pytest.mark.parametrize(
        ("field_name", "expected_max_length"),
        [
            ("name", 100),
            ("background_css", 200),
            ("text_css", 200),
        ],
    )
    def test_field_max_lengths(
        self, field_name: str, expected_max_length: int
    ) -> None:
        """
        Test the max_length of each field.

        :param field_name: The name of the field to test
        :param expected_max_length: The expected max_length of the field
        :return: None
        """
        field = ColorModel._meta.get_field(field_name)
        assert field.max_length == expected_max_length

    def test_cannot_instantiate_abstract_model(self) -> None:
        """
        Test that ColorModel cannot be instantiated directly.

        :return: None
        """
        with pytest.raises(TypeError) as exc_info:
            ColorModel()

        # The error message may vary depending on Django version,
        # so we're just checking that an error is raised
        assert "abstract" in str(exc_info.value).lower()

    def test_str_method_inheritance(self, color_model: pytest.fixture) -> None:
        """
        Test that subclasses inherit __str__ method from Model.

        :param color_model: Fixture that provides a concrete
            ColorModel subclass
        :return: None
        """
        # Create an instance of the concrete subclass
        instance = color_model(name="Test Color")

        # Should use the default __str__ from Model
        # The exact format may vary by Django version, so we just check it's
        # not empty
        assert str(instance) != ""
        assert "Test Color" not in str(
            instance
        )  # Default __str__ doesn't use name
