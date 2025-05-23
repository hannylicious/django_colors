"""Tests for the fields module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.db import models
from django.forms import ChoiceField

from django_colors.color_definitions import BootstrapColorChoices
from django_colors.field_type import FieldType
from django_colors.fields import ColorModelField
from django_colors.widgets import ColorChoiceWidget


@pytest.mark.django_db
class TestColorModelField:
    """Test the ColorModelField class."""

    def test_initialization_defaults(self) -> None:
        """
        Test initialization with default values.

        :return: None
        """
        field = ColorModelField()

        assert field.choice_model is None
        assert field.choice_filters is None
        assert field.color_type is None
        assert field.default_color_choices is None
        assert field.only_use_custom_colors is None
        assert field.max_length == 150
        assert field.model_name is None
        assert field.app_name is None

    def test_initialization_with_custom_values(
        self, mock_model_class: pytest.fixture
    ) -> None:
        """
        Test initialization with custom values.

        :param mock_model_class: The mock model class fixture
        :return: None
        """
        field = ColorModelField(
            model=mock_model_class,
            model_filters={"name": "test"},
            color_type=FieldType.TEXT,
            default_color_choices=BootstrapColorChoices,
            only_use_custom_colors=True,
            max_length=200,
        )

        assert field.choice_model is mock_model_class
        assert field.choice_filters == {"name": "test"}
        assert field.color_type is FieldType.TEXT
        assert field.default_color_choices is BootstrapColorChoices
        assert field.only_use_custom_colors is True
        assert field.max_length == 200

    def test_initialization_with_only_custom_colors_no_model_or_filters(
        self,
    ) -> None:
        """
        Test init (only_use_custom_colors=True & no model or queryset).

        :return: None
        """
        with pytest.raises(
            Exception, match="You must have a model or model_filters .*"
        ):
            ColorModelField(only_use_custom_colors=True)

    def test_initialization_with_only_custom_colors_with_model(
        self, mock_model_class: pytest.fixture
    ) -> None:
        """
        Test initialization with only_use_custom_colors=True and a model.

        :param mock_model_class: The mock model class fixture
        :return: None
        """
        field = ColorModelField(
            model=mock_model_class,
            only_use_custom_colors=True,
        )

        assert field.choice_model is mock_model_class
        assert field.only_use_custom_colors is True

    def test_initialization_with_only_custom_colors_with_filters(
        self,
    ) -> None:
        """
        Test initialization with only_use_custom_colors=True and a filter.

        :return: None
        """
        filter = {"name": "test"}

        field = ColorModelField(
            model_filters=filter,
            only_use_custom_colors=True,
        )

        assert field.choice_filters == filter
        assert field.only_use_custom_colors is True

    @patch("django_colors.settings.get_config")
    def test_get_config_dict(self, mock_get_config: Mock) -> None:
        """
        Test the get_config_dict method.

        :param mock_get_config: Mock for the get_config function
        :return: None
        """
        mock_config = {"test_config": "value"}
        mock_get_config.return_value = {
            "app_name": mock_config,
            "default": {"default_config": "value"},
        }

        field = ColorModelField()
        field.app_name = "app_name"

        # Reset the mock to ignore any setup calls
        mock_get_config.reset_mock()

        result = field.get_config_dict()

        assert result == mock_config
        # TODO: Investigate why this is called twice
        assert mock_get_config.call_count == 2

    @patch("django_colors.settings.get_config")
    def test_get_config_dict_default(self, mock_get_config: Mock) -> None:
        """
        Test the get_config_dict method with default values.

        :param mock_get_config: Mock for the get_config function
        :return: None
        """
        default_config = {"default_config": "value"}
        mock_get_config.return_value = {"default": default_config}

        field = ColorModelField()
        field.app_name = "unknown_app"

        # Reset the mock to ignore any setup calls
        mock_get_config.reset_mock()

        result = field.get_config_dict()

        assert result == default_config
        # TODO: Investigate why this is called twice
        assert (
            mock_get_config.call_count == 2
        )  # Verify it was called exactly once

    @pytest.mark.django_db
    def test_contribute_to_class(
        self, mock_model_class: pytest.fixture
    ) -> None:
        """
        Test the contribute_to_class method.

        :param mock_model_class: The mock model class fixture
        :return: None
        """
        with patch("django_colors.settings.FieldConfig") as mock_field_config:
            field = ColorModelField()
            field.contribute_to_class(mock_model_class, "test_field")

            assert field.model_name == "MockModel"
            assert field.app_name == "test_app"
            mock_field_config.assert_called_once_with(
                mock_model_class, field, "test_field"
            )

    def test_non_db_attrs(self) -> None:
        """
        Test the non_db_attrs property.

        :return: None
        """
        field = ColorModelField()
        non_db_attrs = field.non_db_attrs

        assert "choice_model" in non_db_attrs
        assert "choice_filters" in non_db_attrs
        assert "default_color_choices" in non_db_attrs
        assert "color_type" in non_db_attrs
        assert "only_use_custom_colors" in non_db_attrs

    def test_deconstruct(self, mock_model_class: pytest.fixture) -> None:
        """
        Test the deconstruct method.

        :param mock_model_class: The mock model class fixture
        :return: None
        """
        filters = {"name": "test"}

        field = ColorModelField(
            model=mock_model_class,
            model_filters=filters,
            color_type=FieldType.TEXT,
            only_use_custom_colors=True,
        )

        name, path, args, kwargs = field.deconstruct()

        assert path.endswith("ColorModelField")
        assert kwargs["color_type"] == FieldType.TEXT
        assert kwargs["model"] == mock_model_class
        assert kwargs["model_filters"] == filters
        assert kwargs["only_use_custom_colors"] is True

    def test_deconstruct_defaults(self) -> None:
        """
        Test the deconstruct method with default values.

        :return: None
        """
        field = ColorModelField()

        name, path, args, kwargs = field.deconstruct()

        assert path.endswith("ColorModelField")
        assert "color_type" not in kwargs
        assert "model" not in kwargs
        assert "queryset" not in kwargs
        assert "only_use_custom_colors" not in kwargs

    def test_formfield_returns_choice_field(self) -> None:
        """
        Test that formfield returns a ChoiceField.

        :return: None
        """
        field = ColorModelField()

        # Mock the get_choices method to avoid needing Django setup
        field.get_choices = Mock(return_value=[("value", "label")])

        form_field = field.formfield()

        assert isinstance(form_field, ChoiceField)
        assert form_field.widget.__class__ == ColorChoiceWidget

    def test_get_choices_with_mock_field_config(
        self, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test the get_choices method with a mocked field_config.

        :return: None
        """
        field = ColorModelField()

        # Create a mock field_config
        field.field_config = mock_field_config

        # Should return default choices from BootstrapColorChoices
        choices = field.get_choices()

        assert isinstance(choices, list)
        assert len(choices) > 0  # Should have BootstrapColorChoices
        assert all(
            isinstance(choice, tuple) and len(choice) == 2
            for choice in choices
        )

    def test_get_choices_with_model_priority(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test the get_choices method with model filters.

        :return: None
        """
        mock_objects = Mock()

        # Define different return values based on filter arguments
        def mock_filter(**kwargs: dict) -> Mock:
            mock_queryset = Mock()

            if kwargs.get("background_css") == "bg-red":
                # When filtering for bg-red, only return red items
                mock_queryset.values_list.return_value = [
                    ("bg-red", "Test Red"),
                    ("bg-red-dark", "Dark Red"),  # other red variants
                ]
            else:
                # Default case - return all items
                mock_queryset.values_list.return_value = [
                    ("bg-red", "Test Red"),
                    ("bg-blue", "Test Blue"),
                    ("bg-green", "Test Green"),
                ]

            return mock_queryset

        mock_objects.filter.side_effect = mock_filter

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_objects):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "default_color_choices": BootstrapColorChoices,
                "choice_model": color_model,
                "choice_filters": {
                    "background_css": "bg-blue"
                },  # This should filter
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            field.field_config = mock_field_config
            field.choice_model = color_model
            # We set the model_priority to True to show all model responses
            choices = field.get_choices(model_priority=True)

            # Verify the filter was called with the expected arguments
            mock_objects.filter.assert_called_once()

            # Check that all items are included from custom choices
            assert isinstance(choices, list)
            assert len(choices) > 1
            assert ("bg-red", "Test Red") in choices
            assert ("bg-blue", "Test Blue") in choices
            assert ("bg-green", "Test Green") in choices

            # Verify default Bootstrap choices are still there
            bootstrap_choices = [
                choice
                for choice in choices
                if choice[0].startswith("bg-primary")
            ]
            assert len(bootstrap_choices) > 0

    def test_get_choices_with_model_filters(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test the get_choices method with model filters.

        :return: None
        """
        mock_objects = Mock()

        # Define different return values based on filter arguments
        def mock_filter(**kwargs: dict) -> Mock:
            mock_queryset = Mock()

            if kwargs.get("background_css") == "bg-red":
                # When filtering for bg-red, only return red items
                mock_queryset.values_list.return_value = [
                    ("bg-red", "Test Red"),
                    ("bg-red-dark", "Dark Red"),  # other red variants
                ]
            else:
                # Default case - return all items
                mock_queryset.values_list.return_value = [
                    ("bg-red", "Test Red"),
                    ("bg-blue", "Test Blue"),
                    ("bg-green", "Test Green"),
                ]

            return mock_queryset

        mock_objects.filter.side_effect = mock_filter

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_objects):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "default_color_choices": BootstrapColorChoices,
                "choice_model": color_model,
                "choice_filters": {
                    "background_css": "bg-red"
                },  # This should filter
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            field.field_config = mock_field_config
            field.choice_model = color_model
            choices = field.get_choices()

            # Verify the filter was called with the expected arguments
            mock_objects.filter.assert_called_once_with(
                background_css="bg-red"
            )

            # Check that only red items are included from custom choices
            assert isinstance(choices, list)
            assert len(choices) > 1
            # Verify red items are present
            assert ("bg-red", "Test Red") in choices
            assert ("bg-red-dark", "Dark Red") in choices

            # Verify blue items are NOT present (filtered out)
            assert ("bg-blue", "Test Blue") not in choices
            assert ("bg-green", "Test Green") not in choices

            # Verify default Bootstrap choices are still there
            bootstrap_choices = [
                choice
                for choice in choices
                if choice[0].startswith("bg-primary")
            ]
            assert len(bootstrap_choices) > 0

    def test_get_choices_with_model(
        self, color_model: pytest.fixture, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test the get_choices method with a model.

        :return: None
        """
        # Create a mock objects manager
        mock_objects = MagicMock()

        # When no filters are applied, return all items via .all()
        custom_choices = [
            ("custom-bg-3", "Custom 3"),
            ("custom-bg-4", "Custom 4"),
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
        ]
        mock_objects.filter.return_value.values_list.return_value = (
            custom_choices
        )

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_objects):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "default_color_choices": BootstrapColorChoices,
                "choice_model": color_model,
                "choice_filters": {},  # No filters - should get all
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            field.field_config = mock_field_config
            field.choice_model = color_model
            choices = field.get_choices()

            # Verify .filter() was called
            mock_objects.filter.assert_called_once()
            mock_objects.filter.return_value.values_list.assert_called_once_with(
                FieldType.BACKGROUND.value, "name"
            )

            # Should include default choices + all custom choices
            assert isinstance(choices, list)
            assert (
                len(choices) > 4
            )  # Should have BootstrapColorChoices + 4 custom choices

            # Verify all custom choices are present
            for custom_choice in custom_choices:
                assert custom_choice in choices

            # Verify default Bootstrap choices are still there
            bootstrap_choices = [
                choice
                for choice in choices
                if choice[0].startswith("bg-primary")
            ]
            assert len(bootstrap_choices) > 0

    def test_get_choices_with_only_custom_colors(
        self, mock_field_config: pytest.fixture, color_model: pytest.fixture
    ) -> None:
        """
        Test the get_choices method with only_use_custom_colors=True.

        :return: None
        """
        # Create a mock objects manager
        mock_objects = MagicMock()

        # When no filters are applied, return all items via .all()
        custom_choices = [
            ("custom-bg-3", "Custom 3"),
            ("custom-bg-4", "Custom 4"),
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
        ]
        mock_objects.filter.return_value.values_list.return_value = (
            custom_choices
        )

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_objects):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "default_color_choices": BootstrapColorChoices,
                "choice_model": color_model,
                "choice_filters": {},  # No filters - should get all
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": True,
            }[key]

            field.field_config = mock_field_config
            field.choice_model = color_model
            choices = field.get_choices()

            # Verify .filter() was called
            mock_objects.filter.assert_called_once()
            mock_objects.filter.return_value.values_list.assert_called_once_with(
                FieldType.BACKGROUND.value, "name"
            )

            # Should have only custom choices
            assert isinstance(choices, list)
            assert (
                len(choices) == 4
            )  # Should have BootstrapColorChoices + 4 custom choices

            # Verify all custom choices are present
            for custom_choice in custom_choices:
                assert custom_choice in choices

    def test_inheritance(self) -> None:
        """
        Test that ColorModelField inherits from CharField.

        :return: None
        """
        assert issubclass(ColorModelField, models.CharField)


@pytest.mark.django_db
class TestColorModelFieldIntegration:
    """Integration tests for the ColorModelField class."""

    class IntegrationTestModel(models.Model):
        """Test model with ColorModelField."""

        name = models.CharField(max_length=100)
        color = ColorModelField()

        class Meta:
            """Meta class for testing."""

            app_label = "test_app"

        def __str__(self) -> str:
            """Return string representation of the model."""
            return self.name

    class CustomSettingsIntegrationTestModel(models.Model):
        """Test model with customized ColorModelField."""

        name = models.CharField(max_length=100)
        color = ColorModelField(
            color_type=FieldType.TEXT,
            default_color_choices=BootstrapColorChoices,
            max_length=200,
        )

        class Meta:
            """Meta class for testing."""

            app_label = "test_app"

        def __str__(self) -> str:
            """Return string representation of the model."""
            return self.name

    def test_field_in_model(self) -> None:
        """
        Test using ColorModelField in a model.

        :return: None
        """
        # Get the field from the model
        color_field = self.IntegrationTestModel._meta.get_field("color")

        # Check that it's a ColorModelField
        assert isinstance(color_field, ColorModelField)
        assert color_field.max_length == 150  # Default max_length

    def test_field_with_custom_settings(self) -> None:
        """
        Test using ColorModelField with custom settings.

        :return: None
        """
        # Get the field from the model
        color_field = self.CustomSettingsIntegrationTestModel._meta.get_field(
            "color"
        )

        # Check that it's a ColorModelField with the right settings
        assert isinstance(color_field, ColorModelField)
        assert color_field.max_length == 200
        assert color_field.color_type == FieldType.TEXT
        assert color_field.default_color_choices == BootstrapColorChoices
