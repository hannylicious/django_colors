from django.conf import settings
from colors.color_definitions import BootstrapColorChoices, ColorChoices
from django.db.models import Field, Model
from colors.field_type import FieldType


CONFIG_DEFAULTS = {
    "default": {
        "default_color_choices": BootstrapColorChoices,
        "color_type": "BACKGROUND",
        "choice_model": None,
        "choice_queryset": None,
        "only_use_custom_colors": False,
    }
}


def get_config():
    USER_CONFIG = getattr(settings, "COLORS_APP_CONFIG", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG


class FieldConfig:
    _defaults = CONFIG_DEFAULTS.copy()
    config: dict

    # add model and field type annotations
    def __init__(self, model_class=None, field_class=None, field_name=None) -> dict:
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

    def get(self, value: str):
        """Get the value from config"""
        try:
            return self.config[value]
        except KeyError:
            raise ValueError(f"Invalid value provided.")

    def get_settings_config(
        self, django_app_settings: dict, model_class: Model, field_name: str
    ):
        """Get the settings config from django settings."""
        app_label = model_class._meta.app_label
        model_name = model_class.__class__.__name__
        # get the heirarchy from django_app_settings
        hierarchy_settings_config = django_app_settings.get("default", {})
        # update the dict with values from app specific settings
        hierarchy_settings_config.update(django_app_settings.get(app_label, {}))
        # update with model config
        hierarchy_settings_config.update(
            django_app_settings.get(f"{app_label}.{model_name}", {})
        )
        # update with field config
        hierarchy_settings_config.update(
            django_app_settings.get(f"{app_label}.{model_name}.{field_name}", {})
        )
        return hierarchy_settings_config

    def get_field_config(self, field_class: Field) -> dict:
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

    def set_color_choices(self):
        if self.config.get("only_use_custom_colors"):
            if (
                self.config.get("choice_model") is None
                and self.config.get("choice_queryset") is None
            ):
                raise Exception("Cannot use custom colors without a model or queryset.")
            else:
                self.config["default_color_choices"] = ColorChoices

    def cast_color_type(self):
        if isinstance(self.config.get("color_type"), str):
            self.config["color_type"] = FieldType[self.config.get("color_type")]
