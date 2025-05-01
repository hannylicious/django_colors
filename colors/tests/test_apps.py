"""Tests for the colors apps.py."""


class TestColorsConfig:
    """Test the colors app configuration."""

    def test_app_config_name(self) -> None:
        """Test the app config name."""
        from colors.apps import ColorsConfig

        assert ColorsConfig.name == "colors"
        assert ColorsConfig.verbose_name == "Colors"

    def test_app_config_auto_field(self) -> None:
        """Test auto field setting."""
        from colors.apps import ColorsConfig

        assert (
            ColorsConfig.default_auto_field == "django.db.models.BigAutoField"
        )
