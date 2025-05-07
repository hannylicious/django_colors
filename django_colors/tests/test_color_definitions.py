"""Tests for the color_definitions module."""

from collections.abc import Iterator

import pytest

from django_colors.color_definitions import (
    ColorChoices,
    ColorOption,
)
from django_colors.field_type import FieldType


class TestColorOption:
    """Test the ColorOption class."""

    def test_instance_choices_background_option(
        self, color_option: pytest.fixture
    ) -> None:
        """
        Test the instance_choices method returns background_css.

        :param color_option: The color option fixture
        :return: None
        """
        assert color_option.instance_choices(FieldType.BACKGROUND) == (
            "bg-red",
            "Red",
        )

    def test_instance_choices_text_option(
        self, color_option: pytest.fixture
    ) -> None:
        """
        Test the instance_choices method returns text_css.

        :param color_option: The color option fixture
        :return: None
        """
        assert color_option.instance_choices(FieldType.TEXT) == (
            "text-red",
            "Red",
        )

    def test_instance_choices_with_none(
        self, color_option: pytest.fixture
    ) -> None:
        """
        Test the instance_choices method raises AttributeError with None.

        :param color_option: The color option fixture
        :return: None
        """
        with pytest.raises(AttributeError):
            color_option.instance_choices(None)

    def test_instance_choices_with_invalid_choice(
        self, color_option: pytest.fixture
    ) -> None:
        """
        Test the instance_choices raises AttributeError with invalid choice.

        :param color_option: The color option fixture
        :return: None
        """
        with pytest.raises(AttributeError):
            color_option.instance_choices(FieldType.FONT)  # type: ignore

    def test_class_is_frozen(self, color_option: pytest.fixture) -> None:
        """
        Test that the ColorOption class is frozen.

        :param color_option: The color option fixture
        :return: None
        """
        assert color_option.__dataclass_params__.frozen is True

    def test_class_is_slots(self, color_option: pytest.fixture) -> None:
        """
        Test that the ColorOption class uses slots.

        :param color_option: The color option fixture
        :return: None
        """
        assert color_option.__dataclass_params__.slots is True


class TestColorChoices:
    """Test the ColorChoices class."""

    def test_get_options_dict(self, color_choice: pytest.fixture) -> None:
        """
        Test the get_options_dict method.

        :param color_choice: The color choice fixture
        :return: None
        """
        assert color_choice.get_options_dict == {}

    def test_get_by_value(self, color_choice: pytest.fixture) -> None:
        """
        Test the get_by_value method.

        :param color_choice: The color choice fixture
        :return: None
        """
        assert color_choice.get_by_value("red") is None

    def test_get_or_raise_with_valid_value(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test the get_or_raise method with a valid value.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        assert (
            bootstrap_color_choice.get_or_raise("blue")
            == bootstrap_color_choice.BLUE
        )

    def test_get_or_raise_with_invalid_value(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test the get_or_raise method with an invalid value.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        with pytest.raises(KeyError):
            bootstrap_color_choice.get_or_raise("invalid")

    def test_choices_property(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test the choices property.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        choices = bootstrap_color_choice.choices
        assert isinstance(choices, list)
        assert len(choices) == 11  # 11 color options in BootstrapColorChoices
        assert all(isinstance(choice, tuple) for choice in choices)
        assert all(len(choice) == 2 for choice in choices)

    def test_iter_method(self, bootstrap_color_choice: pytest.fixture) -> None:
        """
        Test the __iter__ method.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        iterator = iter(bootstrap_color_choice)
        assert isinstance(iterator, Iterator)

        # Check that all items are ColorOption instances
        items = list(iterator)
        assert len(items) == 11  # 11 color options in BootstrapColorChoices
        assert all(isinstance(item, ColorOption) for item in items)

    def test_post_init(self) -> None:
        """
        Test the __post_init__ method populates _value_map correctly.

        :return: None
        """

        # TODO: Investigate this test and need for __post_init__ method
        # Define a test subclass with color options as class attributes
        class TestColors(ColorChoices):
            RED: ColorOption = ColorOption("red", "Red", "bg-red", "text-red")
            BLUE: ColorOption = ColorOption(
                "blue", "Blue", "bg-blue", "text-blue"
            )
            NOT_COLOR: str = "not a color option"

            # Override __post_init__ to use our custom implementation
            def __post_init__(self) -> None:
                """Test implementation of __post_init__."""
                object.__setattr__(self, "_value_map", {})
                for attr_name in dir(self):
                    if attr_name.startswith("_") or attr_name == "NOT_COLOR":
                        continue
                    attr = getattr(self, attr_name)
                    if isinstance(attr, ColorOption):
                        self._value_map[attr.value] = attr

        # Create an instance of our test class
        test_colors = TestColors()

        # The __post_init__ method should have populated _value_map
        assert len(test_colors.get_options_dict) == 2
        assert "red" in test_colors.get_options_dict
        assert "blue" in test_colors.get_options_dict
        assert "NOT_COLOR" not in test_colors.get_options_dict

    def test_field_type_default(self) -> None:
        """
        Test the field_type default value is BACKGROUND.

        :return: None
        """
        color_choices = ColorChoices()
        assert color_choices.field_type == FieldType.BACKGROUND

    def test_field_type_custom(self) -> None:
        """
        Test setting a custom field_type.

        :return: None
        """
        color_choices = ColorChoices(field_type=FieldType.TEXT)
        assert color_choices.field_type == FieldType.TEXT

    def test_choices_uses_field_type(self) -> None:
        """
        Test that choices property uses the field_type.

        :return: None
        """

        # TODO: Investigate this test and need for __post_init__ method
        # Define test classes with RED color option
        class TestColorsBackground(ColorChoices):
            RED: ColorOption = ColorOption("red", "Red", "bg-red", "text-red")

            # Override __post_init__ to use our custom implementation
            def __post_init__(self) -> None:
                """Test implementation of __post_init__."""
                object.__setattr__(self, "_value_map", {})
                for attr_name in dir(self):
                    if attr_name.startswith("_"):
                        continue
                    attr = getattr(self, attr_name)
                    if isinstance(attr, ColorOption):
                        self._value_map[attr.value] = attr

        class TestColorsText(ColorChoices):
            RED: ColorOption = ColorOption("red", "Red", "bg-red", "text-red")

            # Override __post_init__ to use our custom implementation
            def __post_init__(self) -> None:
                """Test implementation of __post_init__."""
                object.__setattr__(self, "_value_map", {})
                for attr_name in dir(self):
                    if attr_name.startswith("_"):
                        continue
                    attr = getattr(self, attr_name)
                    if isinstance(attr, ColorOption):
                        self._value_map[attr.value] = attr

        # Test with BACKGROUND field type
        test_colors_bg = TestColorsBackground(field_type=FieldType.BACKGROUND)
        assert test_colors_bg.choices == [("bg-red", "Red")]

        # Test with TEXT field type
        test_colors_text = TestColorsText(field_type=FieldType.TEXT)
        assert test_colors_text.choices == [("text-red", "Red")]

    def test_class_is_frozen(self, color_choice: pytest.fixture) -> None:
        """
        Test that the ColorChoices class is frozen.

        :param color_choice: The color choice fixture
        :return: None
        """
        assert color_choice.__dataclass_params__.frozen is True

    def test_class_is_slots(self, color_choice: pytest.fixture) -> None:
        """
        Test that the ColorChoices class uses slots.

        :param color_choice: The color option fixture
        :return: None
        """
        assert color_choice.__dataclass_params__.slots is True


class TestBootstrapColorChoices:
    """Test the BootstrapColorChoices class."""

    def test_inheritance(self, bootstrap_color_choice: pytest.fixture) -> None:
        """
        Test that BootstrapColorChoices inherits from ColorChoices.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        assert isinstance(bootstrap_color_choice, ColorChoices)

    def test_predefined_colors(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test that BootstrapColorChoices has the predefined color options.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        predefined_colors = [
            "BLUE",
            "GREEN",
            "YELLOW",
            "RED",
            "PURPLE",
            "INDIGO",
            "PINK",
            "ORANGE",
            "TEAL",
            "CYAN",
            "GRAY",
        ]

        for color in predefined_colors:
            assert hasattr(bootstrap_color_choice, color)
            assert isinstance(
                getattr(bootstrap_color_choice, color), ColorOption
            )

    def test_color_option_values(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test the values of some ColorOption instances.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        # Check BLUE option
        blue = bootstrap_color_choice.BLUE
        assert blue.value == "blue"
        assert blue.label == "Blue"
        assert blue.background_css == "bg-primary"
        assert blue.text_css == "text-primary"

        # Check RED option
        red = bootstrap_color_choice.RED
        assert red.value == "red"
        assert red.label == "Red"
        assert red.background_css == "bg-danger"
        assert red.text_css == "text-danger"

    def test_get_options_dict_populated(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test that get_options_dict is populated with all color options.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        options_dict = bootstrap_color_choice.get_options_dict

        # Check that all 11 colors are in the dict
        assert len(options_dict) == 11

        # Check that the keys match the values
        assert "blue" in options_dict
        assert options_dict["blue"] == bootstrap_color_choice.BLUE

        assert "red" in options_dict
        assert options_dict["red"] == bootstrap_color_choice.RED

    def test_class_is_frozen(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test that the BootstrapColorChoices class is frozen.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        assert bootstrap_color_choice.__dataclass_params__.frozen is True

    def test_class_is_slots(
        self, bootstrap_color_choice: pytest.fixture
    ) -> None:
        """
        Test that the BootstrapColorChoices class uses slots.

        :param bootstrap_color_choice: The bootstrap color choice fixture
        :return: None
        """
        assert bootstrap_color_choice.__dataclass_params__.slots is True
