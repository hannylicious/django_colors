"""Tests for the settings module."""

from unittest.mock import ANY, Mock, patch

import pytest

from django_colors.color_definitions import BootstrapColorChoices, ColorChoices
from django_colors.field_type import FieldType
from django_colors.settings import CONFIG_DEFAULTS, FieldConfig, get_config


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
        assert "choice_filters" in default_config
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
        assert default_config["choice_filters"] == {}
        assert default_config["only_use_custom_colors"] is False


class TestGetConfig:
    """Test the get_config function."""

    @patch("django_colors.settings.getattr")
    def test_get_config_with_no_user_config(self, mock_getattr: Mock) -> None:
        """
        Test get_config when no user config is provided.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        mock_getattr.return_value = {}

        config = get_config()

        assert config == CONFIG_DEFAULTS
        mock_getattr.assert_called_once_with(ANY, "COLORS_APP_CONFIG", {})

    @patch("django_colors.settings.getattr")
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
        mock_getattr.assert_called_once_with(ANY, "COLORS_APP_CONFIG", {})

    @patch("django_colors.settings.getattr")
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

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_init_with_defaults_only(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test initialization with defaults only.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        # Should use the defaults
        assert (
            field_config.config["default_color_choices"]
            == BootstrapColorChoices
        )
        assert field_config.config["color_type"] == FieldType.BACKGROUND
        assert field_config.config["choice_model"] is None
        assert field_config.config["choice_filters"] == {}
        assert field_config.config["only_use_custom_colors"] is False

    @patch("django_colors.settings.get_config")
    def test_init_with_django_settings(self, mock_get_config: Mock) -> None:
        """
        Test initialization with Django settings.

        :param mock_get_config: Mock for the get_config function
        :return: None
        """
        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

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
                "only_use_custom_colors": False,
            },
            "test_app": {"default_color_choices": ColorChoices},
        }

        # Set up the patched get_config to return our settings
        mock_get_config.return_value = django_settings

        # Patch the get_settings_config method to return our custom settings
        with (
            patch.object(
                FieldConfig, "get_settings_config"
            ) as mock_get_settings_config,
            patch.object(FieldConfig, "get_field_config", return_value={}),
        ):
            # Setup the mock to return app-specific settings
            mock_get_settings_config.return_value = {
                "default_color_choices": ColorChoices,
                "color_type": "TEXT",
                "only_use_custom_colors": False,
            }

            # Create the field config
            field_config = FieldConfig(model_class, field_class, "test_field")

        # Should prioritize settings from the Django settings
        assert field_config.config["default_color_choices"] == ColorChoices
        assert field_config.config["color_type"] == FieldType.TEXT
        assert field_config.config["only_use_custom_colors"] is False

    @patch("django_colors.settings.getattr")
    def test_init_with_field_config(self, mock_getattr: Mock) -> None:
        """
        Test initialization with field configuration.

        :param mock_getattr: Mock for the getattr function
        :return: None
        """
        # Create mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        # Create mock field class with configuration
        field_class = Mock()
        field_class.default_color_choices = ColorChoices
        field_class.color_type = FieldType.TEXT
        field_class.choice_model = None
        field_class.choice_queryset = None
        field_class.only_use_custom_colors = False

        # Mock Django settings
        mock_getattr.return_value = {}

        # Prepare the expected field config result
        expected_field_config = {
            "default_color_choices": ColorChoices,
            "color_type": FieldType.TEXT,
            "only_use_custom_colors": False,
        }

        # Mock get_field_config to return our expected result
        with (
            patch.object(FieldConfig, "get_settings_config", return_value={}),
            patch.object(
                FieldConfig,
                "get_field_config",
                return_value=expected_field_config,
            ),
        ):
            field_config = FieldConfig(model_class, field_class, "test_field")

        # Should prioritize field configuration
        assert field_config.config["default_color_choices"] is ColorChoices
        assert field_config.config["color_type"] == FieldType.TEXT
        assert field_config.config["only_use_custom_colors"] is False

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_get_method_valid_key(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test get method with a valid key.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        value = field_config.get("default_color_choices")

        assert value == BootstrapColorChoices

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_get_method_invalid_key(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test get method with an invalid key.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        with pytest.raises(KeyError):
            field_config.get("invalid_key")

    def test_get_settings_config_hierarchy(self) -> None:
        """
        Test the get_settings_config method respects the hierarchy.

        :return: None
        """
        # Create test model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
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

        # Create a field config instance without init
        field_config = FieldConfig.__new__(FieldConfig)

        # Manually implement the method to test it directly
        hierarchy_settings_config = {}

        # Copy values from default
        hierarchy_settings_config.update(django_settings.get("default", {}))

        # Update with app-specific settings
        hierarchy_settings_config.update(django_settings.get("test_app", {}))

        # Update with model-specific settings
        model_key = (
            f"{model_class._meta.app_label}.{model_class.__class__.__name__}"
        )
        hierarchy_settings_config.update(django_settings.get(model_key, {}))

        # Update with field-specific settings
        field_key = f"{model_key}.test_field"
        hierarchy_settings_config.update(django_settings.get(field_key, {}))

        # Now test the actual method
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

        # Create the field config directly (no initialization needed)
        field_config = FieldConfig.__new__(FieldConfig)

        # Call the get_field_config method directly
        result = field_config.get_field_config(field_class)

        # Should include only non-None values
        assert result["default_color_choices"] == ColorChoices
        assert result["color_type"] == FieldType.TEXT
        assert result["only_use_custom_colors"] is True
        assert "choice_model" not in result
        assert "choice_queryset" not in result

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_set_color_choices_with_custom_colors_no_model_or_queryset(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test set_color_choices (only_use_custom_colors & no model or queryset).

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        field_config.config["only_use_custom_colors"] = True
        field_config.config["choice_model"] = None
        field_config.config["choice_filters"] = None

        with pytest.raises(Exception, match="Cannot use custom colors .*"):
            field_config.set_color_choices()

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_set_color_choices_with_custom_colors_and_model(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test set_color_choices with only_use_custom_colors=True and a model.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        field_config.config["only_use_custom_colors"] = True
        field_config.config["choice_model"] = Mock()
        field_config.config["default_color_choices"] = BootstrapColorChoices

        field_config.set_color_choices()

        # Should change default_color_choices to ColorChoices
        assert field_config.config["default_color_choices"] == ColorChoices

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_cast_color_type_with_string(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test cast_color_type with a string value.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        field_config.config["color_type"] = "TEXT"

        field_config.cast_color_type()

        # Should cast the string to a FieldType enum value
        assert field_config.config["color_type"] == FieldType.TEXT

    @patch("django_colors.settings.FieldConfig.get_settings_config")
    @patch("django_colors.settings.getattr")
    def test_cast_color_type_with_enum_value(
        self, mock_getattr: Mock, mock_get_settings_config: Mock
    ) -> None:
        """
        Test cast_color_type with an already cast enum value.

        :param mock_getattr: Mock for the getattr function
        :param mock_get_settings_config: Mock for the get_settings_config
            method
        :return: None
        """
        # Mock Django settings
        mock_getattr.return_value = {}
        # Mock the get_settings_config method to return empty dict
        mock_get_settings_config.return_value = {}

        # Create a mock model class with _meta
        model_class = Mock()
        model_class._meta = Mock()
        model_class._meta.app_label = "test_app"
        model_class.__class__.__name__ = "TestModel"

        field_config = FieldConfig(
            model_class=model_class,
            field_class=Mock(),
            field_name="test_field",
        )

        field_config.config["color_type"] = FieldType.BACKGROUND

        field_config.cast_color_type()

        # Should keep the enum value as is
        assert field_config.config["color_type"] == FieldType.BACKGROUND


class TestFieldConfigStringResolution:
    """Test string resolution functionality in FieldConfig."""

    @patch("django.apps.apps.get_model")
    def test_lazy_model_resolution_from_string(
        self, mock_get_model: pytest.fixture
    ) -> None:
        """Test that string model references are lazily resolved."""
        # Create a real FieldConfig instance (not mocked)
        # but mock the Django model resolution
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with string model reference
        mock_field = Mock()
        mock_field.choice_model = "testapp.TestModel"
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        # Create field config with string model reference
        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # Access the choice_model property - should trigger resolution
        resolved_model = config_instance.choice_model

        # Verify model was resolved correctly
        mock_get_model.assert_called_once_with("testapp", "TestModel")
        assert resolved_model is mock_model

        # Access again - should use cached value
        resolved_model_2 = config_instance.choice_model
        assert resolved_model_2 is mock_model
        # get_model should still only be called once due to caching
        assert mock_get_model.call_count == 1

    def test_invalid_string_model_reference(self) -> None:
        """Test handling of invalid string model references."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with invalid string model reference
        mock_field = Mock()
        mock_field.choice_model = "invalid_format"  # Missing dot separator
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        with pytest.raises(ValueError, match="Invalid model reference"):
            _ = config_instance.choice_model

    @patch("django.apps.apps.get_model")
    def test_has_choice_model_method(
        self, mock_get_model: pytest.fixture
    ) -> None:
        """Test the has_choice_model method doesn't trigger resolution."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with string model reference
        mock_field = Mock()
        mock_field.choice_model = "testapp.TestModel"
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        # Test with string model reference
        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # has_choice_model should return True without calling get_model
        assert config_instance.has_choice_model() is True
        mock_get_model.assert_not_called()

        # Test with None
        config_instance.config["choice_model"] = None
        assert config_instance.has_choice_model() is False
        mock_get_model.assert_not_called()

        # Test with actual model class
        mock_model = Mock()
        config_instance.config["choice_model"] = mock_model
        assert config_instance.has_choice_model() is True
        mock_get_model.assert_not_called()

    @patch("django.apps.apps.get_model")
    def test_model_not_found_error(
        self, mock_get_model: pytest.fixture
    ) -> None:
        """Test handling when string model reference can't be resolved."""
        # Make get_model raise LookupError (built-in Python exception)
        mock_get_model.side_effect = LookupError("Model not found")

        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with non-existent model reference
        mock_field = Mock()
        mock_field.choice_model = "testapp.NonExistentModel"
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        with pytest.raises(ValueError, match="Invalid model reference"):
            _ = config_instance.choice_model

    def test_choice_model_with_actual_model_class(self) -> None:
        """Test choice_model property when config contains a model class."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create a mock model that will be stored in config
        mock_choice_model = Mock()

        # Create mock field with actual model class (not string)
        mock_field = Mock()
        mock_field.choice_model = mock_choice_model  # Already a model class
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # This should return the model class directly without resolution
        result = config_instance.choice_model
        assert result is mock_choice_model

    def test_choice_model_with_none_value(self) -> None:
        """Test choice_model property when config contains None."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with None choice_model
        mock_field = Mock()
        mock_field.choice_model = None
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = None
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # This should return None directly
        result = config_instance.choice_model
        assert result is None

    def test_default_color_choices_string_resolution(self) -> None:
        """Test default_color_choices property resolves string imports."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with string reference to color choices
        mock_field = Mock()
        mock_field.choice_model = None
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = (
            "django_colors.color_definitions.BootstrapColorChoices"
        )
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # This should resolve the string to the actual class
        result = config_instance.default_color_choices
        assert result is BootstrapColorChoices

    def test_default_color_choices_with_class_object(self) -> None:
        """Test default_color_choices property when config contains a class."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with actual class (not string)
        mock_field = Mock()
        mock_field.choice_model = None
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = BootstrapColorChoices
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        # This should return the class directly
        result = config_instance.default_color_choices
        assert result is BootstrapColorChoices

    def test_invalid_default_color_choices_string(self) -> None:
        """Test handling of invalid default_color_choices string references."""
        # Create a mock model class to pass to FieldConfig init
        mock_model_class = Mock()
        mock_model_class._meta.app_label = "testapp"
        mock_model_class.__class__.__name__ = "TestModel"

        # Create mock field with invalid string reference
        mock_field = Mock()
        mock_field.choice_model = None
        mock_field.choice_filters = None
        mock_field.color_type = None
        mock_field.default_color_choices = "nonexistent.module.ClassName"
        mock_field.only_use_custom_colors = None

        config_instance = FieldConfig(
            mock_model_class, mock_field, "test_field"
        )

        with pytest.raises(ValueError, match="Invalid colors reference"):
            _ = config_instance.default_color_choices
