"""Tests for the field_type module."""

from enum import Enum

import pytest

from django_colors.field_type import FieldType


class TestFieldType:
    """Test the FieldType enum class."""

    def test_field_type_is_enum(self) -> None:
        """
        Test that FieldType is an Enum class.

        :return: None
        """
        assert issubclass(FieldType, Enum)

    def test_field_type_values(self) -> None:
        """
        Test that FieldType has the expected values.

        :return: None
        """
        assert FieldType.BACKGROUND.value == "background_css"
        assert FieldType.TEXT.value == "text_css"

    def test_field_type_names(self) -> None:
        """
        Test that FieldType has the expected names.

        :return: None
        """
        assert FieldType.BACKGROUND.name == "BACKGROUND"
        assert FieldType.TEXT.name == "TEXT"

    def test_field_type_iteration(self) -> None:
        """
        Test that FieldType can be iterated over.

        :return: None
        """
        field_types = list(FieldType)
        assert FieldType.BACKGROUND in field_types
        assert FieldType.TEXT in field_types

    def test_field_type_lookup_by_value(self) -> None:
        """
        Test that FieldType members can be looked up by value.

        :return: None
        """
        assert FieldType("background_css") == FieldType.BACKGROUND
        assert FieldType("text_css") == FieldType.TEXT

    def test_field_type_lookup_by_invalid_value(self) -> None:
        """
        Test that looking up FieldType with an invalid value raises ValueError.

        :return: None
        """
        # Use the match parameter to check for the specific error message
        with pytest.raises(
            ValueError, match="'invalid_value' is not a valid FieldType"
        ):
            FieldType("invalid_value")

    def test_field_type_attribute_access(self) -> None:
        """
        Test that FieldType values can be accessed as attributes.

        :return: None
        """
        background = FieldType.BACKGROUND
        text = FieldType.TEXT

        assert background == FieldType.BACKGROUND
        assert text == FieldType.TEXT

    def test_field_type_hashable(self) -> None:
        """
        Test that FieldType members are hashable and can be used as dict keys.

        :return: None
        """
        test_dict = {
            FieldType.BACKGROUND: "background value",
            FieldType.TEXT: "text value",
        }

        assert test_dict[FieldType.BACKGROUND] == "background value"
        assert test_dict[FieldType.TEXT] == "text value"
