"""Tests for the settings module."""

from unittest.mock import Mock, patch

import pytest
from django.db import models

from colors.color_definitions import BootstrapColorChoices, ColorChoices
from colors.field_type import FieldType
from colors.settings import CONFIG_DEFAULTS, FieldConfig, get_config


class TestConfigDefaults:
    """Test the CONFIG_DEFAULTS dictionary."""

    def test_defaults_structure(self) -> None:
        """
        Test the structure of the CONFIG_DEFAULTS dictionary.

        :return: None
        """
        assert isinstance(CONFIG_DEFAULTS, dict)
        assert "default" in CONFIG_DEFAULTS
        default_config = CONFIG_DEFAULTS["default"]

        assert "default_color_choices" in default_config
        assert "color_type" in default_config
        assert "choice_model" in default_config
        assert "choice_queryset" in default_config
        assert "only_use_custom_colors" in default_config

    def test_defaults_values(self) -> None:
        """
        Test the values in the CONFIG_DEFAULTS dictionary.

        :return: None
        """
        default_config = CONFIG_DEFAULTS["default"]

        assert default_config["default_color_choices"] == BootstrapColorChoices
        assert default_config["color_type"] == "BACKGROUND"
        assert default_config["choice_model"] is None
        assert default_config["choice_queryset"] is None
        assert default_config["only_use_custom_colors"] is False


class TestGetConfig:
    """Test the get_config function."""

    @patch("colors.settings.getattr")
    def test_get_config_with_no_user_config(self, mock_getattr: Mock) -> None:
        """
        Test get_config when no user config is provided.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        mock_getattr.return_value = {}

        config = get_config()

        assert config == CONFIG_DEFAULTS
        mock_getattr.assert_called_once_with(
            mock_getattr.return_value, "COLORS_APP_CONFIG", {}
        )

    @patch("colors.settings.getattr")
    def test_get_config_with_user_config(self, mock_getattr: Mock) -> None:
        """
        Test get_config when user config is provided.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        user_config = {
            "default": {
                "color_type": "TEXT",
                "only_use_custom_colors": True,
            },
            "custom_app": {"default_color_choices": ColorChoices},
        }
        mock_getattr.return_value = user_config

        config = get_config()

        expected_config = CONFIG_DEFAULTS.copy()
        expected_config.update(user_config)

        assert config == expected_config
        mock_getattr.assert_called_once_with(
            mock_getattr.return_value, "COLORS_APP_CONFIG", {}
        )

    @patch("colors.settings.getattr")
    def test_get_config_does_not_modify_defaults(
        self, mock_getattr: Mock
    ) -> None:
        """
        Test that get_config does not modify CONFIG_DEFAULTS.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        defaults_before = CONFIG_DEFAULTS.copy()
        user_config = {
            "default": {
                "color_type": "TEXT",
            }
        }
        mock_getattr.return_value = user_config

        get_config()

        assert CONFIG_DEFAULTS == defaults_before


class TestFieldConfig:
    """Test the FieldConfig class."""

    def test_init_with_defaults_only(self) -> None:
        """
        Test initialization with defaults only.

        :return: None
        """
        field_config = FieldConfig()

        # Should use the defaults
        assert (
            field_config.config["default_color_choices"]
            == BootstrapColorChoices
        )
        assert field_config.config["color_type"] == FieldType.BACKGROUND
        assert field_config.config["choice_model"] is None
        assert field_config.config["choice_queryset"] is None
        assert field_config.config["only_use_custom_colors"] is False

    @patch("colors.settings.getattr")
    def test_init_with_django_settings(self, mock_getattr: Mock) -> None:
        """
        Test initialization with Django settings.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """

        # Create test model class
        class TestModel(models.Model):
            class Meta:
                app_label = "test_app"

            def __str__(self) -> str:
                return "TestModel"

        # Create mock field class
        field_class = Mock()
        field_class.default_color_choices = None
        field_class.color_type = None
        field_class.choice_model = None
        field_class.choice_queryset = None
        field_class.only_use_custom_colors = None

        # Setup Django settings
        django_settings = {
            "default": {
                "color_type": "TEXT",
                "only_use_custom_colors": True,
            },
            "test_app": {"default_color_choices": ColorChoices},
        }
        mock_getattr.return_value = django_settings

        field_config = FieldConfig(TestModel, field_class, "test_field")

        # Should prioritize settings from the Django settings
        assert field_config.config["default_color_choices"] == ColorChoices
        assert field_config.config["color_type"] == FieldType.TEXT
        assert field_config.config["only_use_custom_colors"] is True

    def test_init_with_field_config(self) -> None:
        """
        Test initialization with field configuration.

        :return: None
        """
        # Create mock model class
        model_class = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        # Create mock field class with configuration
        field_class = Mock()
        field_class.default_color_choices = ColorChoices
        field_class.color_type = FieldType.TEXT
        field_class.choice_model = None
        field_class.choice_queryset = None
        field_class.only_use_custom_colors = True

        # Mock Django settings
        with patch("colors.settings.getattr", return_value={}):
            field_config = FieldConfig(model_class, field_class, "test_field")

        # Should prioritize field configuration
        assert field_config.config["default_color_choices"] == ColorChoices
        assert field_config.config["color_type"] == FieldType.TEXT
        assert field_config.config["only_use_custom_colors"] is True

    def test_get_method_valid_key(self) -> None:
        """
        Test get method with a valid key.

        :return: None
        """
        field_config = FieldConfig()

        value = field_config.get("default_color_choices")

        assert value == BootstrapColorChoices

    def test_get_method_invalid_key(self) -> None:
        """
        Test get method with an invalid key.

        :return: None
        """
        field_config = FieldConfig()

        with pytest.raises(KeyError):
            field_config.get("invalid_key")

    @patch("colors.settings.getattr")
    def test_get_settings_config_hierarchy(self, mock_getattr: Mock) -> None:
        """
        Test the get_settings_config method respects the hierarchy.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        # Create test model class
        model_class = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        # Setup Django settings with hierarchy
        django_settings = {
            "default": {
                "color_type": "TEXT",
            },
            "test_app": {
                "color_type": "BACKGROUND",
            },
            "test_app.TestModel": {
                "default_color_choices": ColorChoices,
            },
            "test_app.TestModel.test_field": {
                "only_use_custom_colors": True,
            },
        }

        field_config = FieldConfig()
        result = field_config.get_settings_config(
            django_settings, model_class, "test_field"
        )

        # Should apply settings in order (default -> app -> model -> field)
        assert result["color_type"] == "BACKGROUND"  # From app level
        assert (
            result["default_color_choices"] == ColorChoices
        )  # From model level
        assert result["only_use_custom_colors"] is True  # From field level

    def test_get_field_config(self) -> None:
        """
        Test the get_field_config method.

        :return: None
        """
        # Create mock field class with some configurations
        field_class = Mock()
        field_class.default_color_choices = ColorChoices
        field_class.color_type = FieldType.TEXT
        field_class.choice_model = None
        field_class.choice_queryset = None
        field_class.only_use_custom_colors = True

        field_config = FieldConfig()
        result = field_config.get_field_config(field_class)

        # Should include only non-None values
        assert result["default_color_choices"] == ColorChoices
        assert result["color_type"] == FieldType.TEXT
        assert result["only_use_custom_colors"] is True
        assert "choice_model" not in result
        assert "choice_queryset" not in result

    def test_set_color_choices_with_custom_colors_no_model_or_queryset(
        self,
    ) -> None:
        """
        Test set_color_choices (only_use_custom_colors & no model or queryset).

        :return: None
        """
        field_config = FieldConfig()
        field_config.config["only_use_custom_colors"] = True
        field_config.config["choice_model"] = None
        field_config.config["choice_queryset"] = None

        with pytest.raises(Exception, match="Cannot use custom colors .*"):
            field_config.set_color_choices()

    def test_set_color_choices_with_custom_colors_and_model(self) -> None:
        """
        Test set_color_choices with only_use_custom_colors=True and a model.

        :return: None
        """
        field_config = FieldConfig()
        field_config.config["only_use_custom_colors"] = True
        field_config.config["choice_model"] = Mock()
        field_config.config["default_color_choices"] = BootstrapColorChoices

        field_config.set_color_choices()

        # Should change default_color_choices to ColorChoices
        assert field_config.config["default_color_choices"] == ColorChoices

    def test_cast_color_type_with_string(self) -> None:
        """
        Test cast_color_type with a string value.

        :return: None
        """
        field_config = FieldConfig()
        field_config.config["color_type"] = "TEXT"

        field_config.cast_color_type()

        # Should cast the string to a FieldType enum value
        assert field_config.config["color_type"] == FieldType.TEXT

    def test_cast_color_type_with_enum_value(self) -> None:
        """
        Test cast_color_type with an already cast enum value.

        :return: None
        """
        field_config = FieldConfig()
        field_config.config["color_type"] = FieldType.BACKGROUND

        field_config.cast_color_type()

        # Should keep the enum value as is
        assert field_config.config["color_type"] == FieldType.BACKGROUND
