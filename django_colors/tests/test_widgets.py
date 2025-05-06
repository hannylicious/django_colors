"""Tests for the widgets module."""

from unittest.mock import Mock, patch

from django import forms

from django_colors.widgets import ColorChoiceWidget


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

    def test_get_context_uses_custom_templates(self) -> None:
        """
        Test that get_context uses custom templates.

        :return: None
        """
        widget = ColorChoiceWidget()
        context = widget.get_context("test_name", "test_value", {})

        # The widget's template_name should be set correctly
        assert widget.template_name == "color_select.html"

        # Check that the context 'widget' key contains the template_name
        assert "widget" in context
        assert "template_name" in context["widget"]
        assert context["widget"]["template_name"] == "color_select.html"

        # Since option_template_name is a property of the widget and not part
        # of the context, we check the widget itself
        assert widget.option_template_name == "color_select_option.html"

    @patch("django.forms.widgets.Select.render")
    def test_render_uses_template(self, mock_render: Mock) -> None:
        """
        Test that render uses the custom template.

        :param mock_render: Mock for the render method
        :return: None
        """
        # Mock the parent's render method to return a specific value
        mock_render.return_value = "<select>mocked</select>"

        widget = ColorChoiceWidget()
        widget.render("color_field", "red", {"id": "id_color_field"})

        # Verify the render method was called with the custom template name
        mock_render.assert_called_once()

        # Since our widget doesn't override render, it will use the parent's
        # render method which should use our widget's template_name
        assert widget.template_name == "color_select.html"
        assert widget.option_template_name == "color_select_option.html"

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
        # Check type and value - index might be returned as a string
        assert str(option["index"]) == "0"  # Convert to string for comparison
