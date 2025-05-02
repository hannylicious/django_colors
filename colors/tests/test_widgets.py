"""Tests for the widgets module."""

from unittest.mock import Mock, patch

from django import forms
from django.forms.renderers import BaseRenderer

from colors.widgets import ColorChoiceWidget


class TestColorChoiceWidget:
    """Test the ColorChoiceWidget class."""

    def test_inheritance(self) -> None:
        """
        Test that ColorChoiceWidget inherits from forms.Select.

        :return: None
        """
        assert issubclass(ColorChoiceWidget, forms.Select)

    def test_initialization_defaults(self) -> None:
        """
        Test initialization with default values.

        :return: None
        """
        widget = ColorChoiceWidget()

        assert widget.template_name == "color_select.html"
        assert widget.option_template_name == "color_select_option.html"

    def test_initialization_with_attrs(self) -> None:
        """
        Test initialization with custom attributes.

        :return: None
        """
        attrs = {"class": "color-select", "data-color-widget": "true"}
        widget = ColorChoiceWidget(attrs=attrs)

        assert widget.attrs == attrs
        assert widget.template_name == "color_select.html"
        assert widget.option_template_name == "color_select_option.html"

    def test_initialization_with_choices(self) -> None:
        """
        Test initialization with choices.

        :return: None
        """
        choices = [("red", "Red"), ("blue", "Blue"), ("green", "Green")]
        widget = ColorChoiceWidget(choices=choices)

        assert widget.choices == choices
        assert widget.template_name == "color_select.html"
        assert widget.option_template_name == "color_select_option.html"

    def test_initialization_with_attrs_and_choices(self) -> None:
        """
        Test initialization with both attrs and choices.

        :return: None
        """
        attrs = {"class": "color-select"}
        choices = [("red", "Red"), ("blue", "Blue")]
        widget = ColorChoiceWidget(attrs=attrs, choices=choices)

        assert widget.attrs == attrs
        assert widget.choices == choices
        assert widget.template_name == "color_select.html"
        assert widget.option_template_name == "color_select_option.html"

    def test_inherited_methods(self) -> None:
        """
        Test that inherited methods from Select are available.

        :return: None
        """
        widget = ColorChoiceWidget()

        # Check that the widget has get_context and render methods from Select
        assert hasattr(widget, "get_context")
        assert hasattr(widget, "render")
        assert hasattr(widget, "optgroups")
        assert hasattr(widget, "create_option")

    @patch("django.forms.widgets.Select.get_context")
    def test_get_context_uses_custom_templates(
        self, mock_get_context: Mock
    ) -> None:
        """
        Test that get_context uses custom templates.

        :param mock_get_context: Mock for the get_context method
        :return: None
        """
        mock_context = {"template_name": "default_select.html"}
        mock_get_context.return_value = mock_context

        widget = ColorChoiceWidget()
        context = widget.get_context("test_name", "test_value", {})

        # Ensure get_context was called on parent class
        mock_get_context.assert_called_once()

        # Check that context has our custom template names
        assert context["template_name"] == "color_select.html"

        # Since option_template_name is a property of the widget and not part
        # of the context, we check the widget itself
        assert widget.option_template_name == "color_select_option.html"

    def test_render_uses_template(self) -> None:
        """
        Test that render uses the custom template.

        :return: None
        """

        # Create a mock renderer that returns a known string
        class MockRenderer(BaseRenderer):
            """
            Mock renderer for testing widget rendering.

            :attribute render: Method to render templates
            """

            def render(
                self, template_name: str, context: dict, request: object = None
            ) -> str:
                """
                Mock render method that returns a formatted string.

                :param template_name: Name of the template to render
                :param context: Context dictionary for the template
                :param request: Optional request object
                :return: Formatted string indicating what would be rendered
                """
                return f"Rendered {template_name}: {context['widget']['name']}"

        widget = ColorChoiceWidget()
        widget.renderer = MockRenderer()

        rendered = widget.render(
            "color_field", "red", {"id": "id_color_field"}
        )

        # Check that our custom template name was used
        assert "Rendered color_select.html with color_field" == rendered

    def test_option_grouping(self) -> None:
        """
        Test that the optgroups method groups options correctly.

        :return: None
        """
        widget = ColorChoiceWidget()
        widget.choices = [
            ("Colors", [("red", "Red"), ("blue", "Blue")]),
            ("Grayscale", [("black", "Black"), ("white", "White")]),
        ]

        optgroups = widget.optgroups("color_field", ["red"])

        # Should have two groups: Colors and Grayscale
        assert len(optgroups) == 2

        # First group should be Colors
        group_name, options, index = optgroups[0]
        assert group_name == "Colors"
        assert len(options) == 2

        # Second group should be Grayscale
        group_name, options, index = optgroups[1]
        assert group_name == "Grayscale"
        assert len(options) == 2

        # Check that option_template_name is set in each option's attrs
        for _, options, _ in optgroups:
            for option in options:
                assert option["template_name"] == "color_select_option.html"

    def test_create_option_with_custom_template(self) -> None:
        """
        Test that create_option sets the custom template name.

        :return: None
        """
        widget = ColorChoiceWidget()
        option = widget.create_option("color_field", "red", "Red", True, 0)

        # Should include the custom template name
        assert option["template_name"] == "color_select_option.html"

        # Other attributes should be present
        assert option["name"] == "color_field"
        assert option["value"] == "red"
        assert option["label"] == "Red"
        assert option["selected"] is True
        assert option["index"] == 0
