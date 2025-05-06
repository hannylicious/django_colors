"""Tests for the django_colors apps.py."""

from django_colors.apps import DjangoColorsConfig


class TestColorsConfig:
    """Test the django_colors app configuration."""

    def test_app_config_name(self) -> None:
        """Test the app config name."""
        assert DjangoColorsConfig.name == "django_colors"
        assert DjangoColorsConfig.verbose_name == "Django Colors"

    def test_app_config_auto_field(self) -> None:
        """Test auto field setting."""
        assert (
            DjangoColorsConfig.default_auto_field
            == "django.db.models.BigAutoField"
        )
