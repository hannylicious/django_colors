"""Configuration management for the django_colors app."""

from typing import Any

from django.conf import settings
from django.db.models import Field, Model

from django_colors.color_definitions import BootstrapColorChoices, ColorChoices
from django_colors.field_type import FieldType

CONFIG_DEFAULTS: dict[str, dict[str, Any]] = {
    "default": {
        "default_color_choices": BootstrapColorChoices,
        "color_type": "BACKGROUND",
        "choice_model": None,
        "choice_queryset": None,
        "only_use_custom_colors": False,
    }
}


def get_config() -> dict[str, Any]:
    """
    Get the configuration for the colors app.

    Combine default configuration with user-provided configuration.

    :returns: Dictionary containing the app configuration
    """
    user_config = getattr(settings, "COLORS_APP_CONFIG", {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config


class FieldConfig:
    """
    Configuration for a color field instance.

    Resolve configuration based on hierarchy:
    field > app settings > defaults
    """

    _defaults: dict[str, dict[str, Any]] = CONFIG_DEFAULTS.copy()
    config: dict[str, Any]

    def __init__(
        self,
        model_class: type[Model] | None = None,
        field_class: Field | None = None,
        field_name: str | None = None,
    ) -> None:
        """
        Initialize field configuration.

        :argument model_class: The model class the field belongs to
        :argument field_class: The field class instance
        :argument field_name: The name of the field
        :returns: None
        """
        self.config = {}
        # hierarchy: field > settings > defaults

        self.config.update(self._defaults["default"])

        # app config
        django_app_settings = getattr(settings, "COLORS_APP_CONFIG", {})
        app_config = self.get_settings_config(
            django_app_settings, model_class, field_name
        )
        self.config.update(app_config)

        # field config
        field_config = self.get_field_config(field_class)
        self.config.update(field_config)

        # Handle setting default_color_choices if only_use_custom_colors
        self.set_color_choices()

        # Set the color_type to the FieldType
        self.cast_color_type()

    def get(self, value: str) -> str | KeyError:
        """
        Get the value from config.

        :argument value: The configuration key to retrieve
        :returns: The value for the specified configuration key
        :raises ValueError: If the key is not found in the configuration
        """
        try:
            return self.config[value]
        except KeyError as error:
            raise KeyError(f"Invalid value provided. {error}") from KeyError

    def get_settings_config(
        self,
        django_app_settings: dict[str, Any],
        model_class: Model,
        field_name: str,
    ) -> dict[str, Any]:
        """
        Get the settings config from django settings.

        Apply configuration inheritance hierarchy from
        default > app > model > field.

        :argument django_app_settings: The Django settings for the app
        :argument model_class: The model class the field belongs to
        :argument field_name: The name of the field
        :returns: Dictionary containing the resolved settings configuration
        """
        app_label = model_class._meta.app_label
        model_name = model_class.__class__.__name__
        # get the hierarchy from django_app_settings
        hierarchy_settings_config = django_app_settings.get("default", {})
        # update the dict with values from app specific settings
        hierarchy_settings_config.update(
            django_app_settings.get(app_label, {})
        )
        # update with model config
        hierarchy_settings_config.update(
            django_app_settings.get(f"{app_label}.{model_name}", {})
        )
        # update with field config
        hierarchy_settings_config.update(
            django_app_settings.get(
                f"{app_label}.{model_name}.{field_name}", {}
            )
        )
        return hierarchy_settings_config

    def get_field_config(self, field_class: Field) -> dict[str, Any]:
        """
        Get the configuration from the field class.

        :argument field_class: The field class to get configuration from
        :returns: Dictionary containing the field's configuration
        """
        required_field_config = [
            "default_color_choices",
            "color_type",
            "choice_model",
            "choice_queryset",
            "only_use_custom_colors",
        ]
        return {
            key: getattr(field_class, key)
            for key in required_field_config
            if getattr(field_class, key)
        }

    def set_color_choices(self) -> None:
        """
        Set the color choices based on configuration.

        If only_use_custom_colors is True, set default_color_choices to
        ColorChoices.

        :returns: None
        :raises Exception: If only_use_custom_colors is True but no model or
            queryset is provided
        """
        if self.config.get("only_use_custom_colors"):
            if (
                self.config.get("choice_model") is None
                and self.config.get("choice_queryset") is None
            ):
                raise Exception(
                    "Cannot use custom colors without a model or queryset."
                )
            else:
                self.config["default_color_choices"] = ColorChoices

    def cast_color_type(self) -> None:
        """
        Cast the color_type string to a FieldType enum value.

        :returns: None
        """
        if isinstance(self.config.get("color_type"), str):
            self.config["color_type"] = FieldType[
                self.config.get("color_type")
            ]
