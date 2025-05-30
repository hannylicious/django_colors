"""Tests for the fields module."""

from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from django.db import models
from django.forms import ChoiceField

from django_colors.color_definitions import BootstrapColorChoices
from django_colors.field_type import FieldType
from django_colors.fields import (
    BLANK_CHOICE_DASH,
    ColorModelField,
    combine_choices,
    sort_choices,
)
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

    def test_initialization_with_string_model_reference(self) -> None:
        """
        Test initialization with string model reference.

        :return: None
        """
        field = ColorModelField(
            model="testapp.TestModel",
            only_use_custom_colors=True,
        )

        assert field.choice_model == "testapp.TestModel"
        assert field.only_use_custom_colors is True

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

    def test_deconstruct_with_string_model(self) -> None:
        """
        Test the deconstruct method with string model reference.

        :return: None
        """
        field = ColorModelField(
            model="testapp.TestModel",
            color_type=FieldType.TEXT,
        )

        name, path, args, kwargs = field.deconstruct()

        assert path.endswith("ColorModelField")
        assert kwargs["model"] == "testapp.TestModel"
        assert kwargs["color_type"] == FieldType.TEXT

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

        # Set up the mock field_config properly
        mock_field_config.get.side_effect = lambda key: {
            "color_type": FieldType.BACKGROUND,
            "choice_filters": {},
            "only_use_custom_colors": False,
        }[key]

        # Mock the choice_model property to return None (using PropertyMock)
        type(mock_field_config).choice_model = PropertyMock(return_value=None)
        # Mock the default_color_choices property
        type(mock_field_config).default_color_choices = PropertyMock(
            return_value=BootstrapColorChoices
        )

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
        """Test the get_choices method with model priority."""
        custom_choices = [
            ("bg-red", "Test Red"),
            ("bg-blue", "Test Blue"),
            ("bg-green", "Test Green"),
        ]

        # Mock the entire objects manager more simply
        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        with patch.object(color_model, "objects", mock_manager):
            field = ColorModelField()

            # Setup field config
            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {
                    "background_css": "bg-blue"
                },  # Should be ignored with model_priority=True
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            # Call with model_priority=True
            choices = field.get_choices(model_priority=True)

            # Verify filter was called with empty dict (model_priority=True)
            mock_manager.filter.assert_called_once_with()

            # Verify results include both default and custom choices
            assert isinstance(choices, list)
            assert len(choices) > 3

            # Check that custom choices are present
            for custom_choice in custom_choices:
                assert custom_choice in choices, (
                    f"Expected {custom_choice} in choices but got: {choices}"
                )

    def test_get_choices_with_model_filters(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test the get_choices method with model filters.

        :return: None
        """
        custom_choices = [
            ("bg-blue", "Test Blue"),
        ]

        # Mock the entire objects manager more simply
        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        with patch.object(color_model, "objects", mock_manager):
            field = ColorModelField()

            # Setup field config
            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {"background_css": "bg-blue"},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            choices = field.get_choices()

            # Verify filter was called with filtering
            mock_manager.filter.assert_called_once_with(
                background_css="bg-blue"
            )

            # Verify results include both default and custom choices
            assert isinstance(choices, list)
            assert len(choices) > 3

            # Check that custom choices are present
            for custom_choice in custom_choices:
                assert custom_choice in choices, (
                    f"Expected {custom_choice} in choices but got: {choices}"
                )
            # Verify blue items are present
            assert ("bg-blue", "Test Blue") in choices

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
        custom_choices = [("bg-test", "Test One"), ("bg-test2", "Test Two")]

        # Mock the entire objects manager more simply
        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_manager):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            # Mock the choice_model property to return the color_model
            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            # Mock the default_color_choices property
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            choices = field.get_choices()

            # Verify .filter() was called
            mock_manager.filter.assert_called_once()
            mock_manager.filter.assert_called_once_with()

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
        custom_choices = [("bg-test", "Test One"), ("bg-test2", "Test Two")]

        # Mock the entire objects manager more simply
        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        # Replace the entire objects manager
        with patch.object(color_model, "objects", mock_manager):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": True,
            }[key]

            # Mock the choice_model property to return the color_model
            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            # Mock the default_color_choices property
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            choices = field.get_choices()

            # Verify .filter() was called
            mock_manager.filter.assert_called_once()
            mock_manager.filter.assert_called_once_with()

            # Should have only custom choices
            assert isinstance(choices, list)
            assert len(choices) == 2

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

    def test_field_with_string_model_reference(self) -> None:
        """
        Test using ColorModelField with string model reference.

        :return: None
        """
        # Create the field directly without embedding it in a model class
        # to avoid triggering model resolution during test collection
        field = ColorModelField(
            model="test_app.TestModel",
            model_filters={"active": True},
        )

        # Check that it's a ColorModelField with string model reference
        assert isinstance(field, ColorModelField)
        assert field.choice_model == "test_app.TestModel"
        assert field.choice_filters == {"active": True}

    def test_field_string_model_integration_with_mocked_resolution(
        self,
    ) -> None:
        """Test string model resolution in a more controlled way."""
        with patch("django.apps.apps.get_model") as mock_get_model:
            # Mock the model resolution
            mock_model = Mock()
            mock_get_model.return_value = mock_model

            # Create a field with string model reference
            field = ColorModelField(model="test_app.MockModel")

            # Create a mock model class for contribute_to_class
            mock_model_class = Mock()
            mock_model_class.__name__ = "TestModel"
            mock_model_class._meta.app_label = "test_app"

            # This should not raise an error
            field.contribute_to_class(mock_model_class, "color_field")

            # Verify the field configuration was set up
            assert hasattr(field, "field_config")
            assert field.model_name == "TestModel"
            assert field.app_name == "test_app"


class TestCombineChoices:
    """Tests for the combine_choices function."""

    def test_combine_choices_defaults_first(self) -> None:
        """Test combine_choices method with defaults_first."""
        layout = "defaults_first"
        queryset_list = [("bg-red", "Red"), ("bg-blue", "Blue")]
        default_list = [("bg-green", "Green"), ("bg-yellow", "Yellow")]

        final_list = combine_choices(layout, default_list, queryset_list)
        for item in default_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        for item in queryset_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        assert len(final_list) == len(default_list) + len(queryset_list)
        assert final_list[0:2] == default_list
        assert final_list[2:] == queryset_list

    def test_combine_choices_custom_first(self) -> None:
        """Test combine_choices method with custom_first layout."""
        layout = "custom_first"
        queryset_list = [("bg-red", "Red"), ("bg-blue", "Blue")]
        default_list = [("bg-green", "Green"), ("bg-yellow", "Yellow")]

        final_list = combine_choices(layout, default_list, queryset_list)
        for item in default_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        for item in queryset_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        assert len(final_list) == len(default_list) + len(queryset_list)
        assert final_list[0:2] == queryset_list
        assert final_list[2:] == default_list

    def test_combine_choices_mixed(self) -> None:
        """Test combine_choices method with mixed layout."""
        layout = "mixed"
        queryset_list = [("bg-red", "Red"), ("bg-blue", "Blue")]
        default_list = [("bg-green", "Green"), ("bg-yellow", "Yellow")]

        final_list = combine_choices(layout, default_list, queryset_list)
        for item in default_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        for item in queryset_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        assert len(final_list) == len(default_list) + len(queryset_list)
        assert final_list[0:2] == default_list
        assert final_list[2:] == queryset_list

    def test_combine_choices_no_layout(self) -> None:
        """Test combine_choices method with no layout."""
        layout = None
        queryset_list = [("bg-red", "Red"), ("bg-blue", "Blue")]
        default_list = [("bg-green", "Green"), ("bg-yellow", "Yellow")]

        final_list = combine_choices(layout, default_list, queryset_list)
        for item in default_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        for item in queryset_list:
            assert item in final_list, (
                f"Expected {item} in final list but got: {final_list}"
            )
        assert len(final_list) == len(default_list) + len(queryset_list)
        assert final_list[0:2] == default_list
        assert final_list[2:] == queryset_list

    def test_get_choices_invalid_layout(
        self, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test get_choices with invalid layout parameter.

        :param mock_field_config: Mock field config fixture
        :return: None
        """
        field = ColorModelField()
        field.field_config = mock_field_config

        with pytest.raises(
            ValueError,
            match="layout must be 'defaults_first', 'custom_first', or 'mixed', got 'invalid_layout'",  # noqa: E501
        ):
            field.get_choices(layout="invalid_layout")

    def test_get_choices_invalid_sort_by(
        self, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test get_choices with invalid sort_by parameter.

        :param mock_field_config: Mock field config fixture
        :return: None
        """
        field = ColorModelField()
        field.field_config = mock_field_config

        with pytest.raises(
            ValueError,
            match="sort_by must be 'label', 'value', or not set, got 'invalid_sort'",  # noqa: E501
        ):
            field.get_choices(sort_by="invalid_sort")

    def test_get_choices_with_predefined_choices_no_blank(self) -> None:
        """
        Test get_choices when self.choices is not None without include_blank.

        :return: None
        """
        predefined_choices = [
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
        ]
        field = ColorModelField(choices=predefined_choices)

        choices = field.get_choices(include_blank=False)

        assert choices == predefined_choices

    def test_get_choices_with_predefined_choices_with_blank(self) -> None:
        """
        Test get_choices when self.choices is not None with include_blank.

        :return: None
        """
        predefined_choices = [
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
        ]
        field = ColorModelField(choices=predefined_choices)

        choices = field.get_choices(include_blank=True)

        # Should return BlankChoiceIterator, which is the expected behavior
        # We can test this by checking the type or behavior
        from django.utils.choices import BlankChoiceIterator

        assert isinstance(choices, BlankChoiceIterator)

    def test_get_choices_with_predefined_choices_custom_blank(self) -> None:
        """
        Test get_choices when self.choices is not None and custom blank choice.

        :return: None
        """
        predefined_choices = [
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
        ]
        field = ColorModelField(choices=predefined_choices)

        choices = field.get_choices(
            include_blank=True, blank_choice="Choose color..."
        )

        from django.utils.choices import BlankChoiceIterator

        assert isinstance(choices, BlankChoiceIterator)

    def test_get_choices_mixed_layout_with_sorting(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test get_choices with mixed layout and sorting.

        :param mock_field_config: Mock field config fixture
        :param color_model: Mock color model fixture
        :return: None
        """
        custom_choices = [("bg-zebra", "Zebra"), ("bg-apple", "Apple")]

        # Mock the entire objects manager
        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        with patch.object(color_model, "objects", mock_manager):
            field = ColorModelField()
            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            # Test mixed layout with sorting by label
            choices = field.get_choices(layout="mixed", sort_by="label")

            assert isinstance(choices, list)
            assert len(choices) > 2

            # Verify custom choices are present
            for custom_choice in custom_choices:
                assert custom_choice in choices

            # Check that choices are sorted by label (second element of tuple)
            # We can't easily verify the exact order due to Bootstrap choices,
            # but we can verify that our custom choices maintain their
            # relationship
            apple_index = next(
                i
                for i, choice in enumerate(choices)
                if choice[0] == "bg-apple"
            )
            zebra_index = next(
                i
                for i, choice in enumerate(choices)
                if choice[0] == "bg-zebra"
            )
            assert apple_index < zebra_index, (
                "Apple should come before Zebra when sorted by label"
            )

    def test_get_choices_with_include_blank(
        self, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test get_choices with include_blank=True.

        :param mock_field_config: Mock field config fixture
        :return: None
        """
        field = ColorModelField()

        mock_field_config.get.side_effect = lambda key: {
            "color_type": FieldType.BACKGROUND,
            "choice_filters": {},
            "only_use_custom_colors": False,
        }[key]

        type(mock_field_config).choice_model = PropertyMock(return_value=None)
        type(mock_field_config).default_color_choices = PropertyMock(
            return_value=BootstrapColorChoices
        )

        field.field_config = mock_field_config

        choices = field.get_choices(include_blank=True)

        assert isinstance(choices, list)
        assert len(choices) > 0
        # First choice should be the blank choice
        assert choices[0] == ("", BLANK_CHOICE_DASH)

    def test_get_choices_with_custom_blank_choice(
        self, mock_field_config: pytest.fixture
    ) -> None:
        """
        Test get_choices with custom blank choice text.

        :param mock_field_config: Mock field config fixture
        :return: None
        """
        field = ColorModelField()

        mock_field_config.get.side_effect = lambda key: {
            "color_type": FieldType.BACKGROUND,
            "choice_filters": {},
            "only_use_custom_colors": False,
        }[key]

        type(mock_field_config).choice_model = PropertyMock(return_value=None)
        type(mock_field_config).default_color_choices = PropertyMock(
            return_value=BootstrapColorChoices
        )

        field.field_config = mock_field_config

        custom_blank = "Select a color..."
        choices = field.get_choices(
            include_blank=True, blank_choice=custom_blank
        )

        assert isinstance(choices, list)
        assert len(choices) > 0
        # First choice should be the custom blank choice
        assert choices[0] == ("", custom_blank)

    def test_get_choices_uses_field_ordering_parameter(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test that get_choices uses field-level ordering parameter.

        :param mock_field_config: Mock field config fixture
        :param color_model: Mock color model fixture
        :return: None
        """
        custom_choices = [("bg-red", "Red"), ("bg-blue", "Blue")]

        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        with patch.object(color_model, "objects", mock_manager):
            # Create field with ordering parameter
            field = ColorModelField(ordering=("name", "-created"))

            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            field.get_choices()

            # Verify order_by was called with field-level ordering
            mock_manager.filter.return_value.distinct.return_value.order_by.assert_called_with(
                "name", "-created"
            )

    def test_get_choices_uses_field_layout_parameter(
        self,
        mock_field_config: pytest.fixture,
        color_model: pytest.fixture,
    ) -> None:
        """
        Test that get_choices uses field-level layout parameter.

        :param mock_field_config: Mock field config fixture
        :param color_model: Mock color model fixture
        :return: None
        """
        custom_choices = [("bg-field", "A Color")]

        mock_manager = MagicMock()
        # fmt: off
        mock_manager.\
        filter.\
        return_value.\
        distinct.\
        return_value.\
        order_by.\
        return_value.\
        values_list.\
        return_value = custom_choices
        # fmt: on

        with patch.object(color_model, "objects", mock_manager):
            # Create field with layout parameter set to custom_first
            field = ColorModelField(layout="custom_first")

            mock_field_config.get.side_effect = lambda key: {
                "choice_filters": {},
                "color_type": FieldType.BACKGROUND,
                "only_use_custom_colors": False,
            }[key]

            type(mock_field_config).choice_model = PropertyMock(
                return_value=color_model
            )
            type(mock_field_config).default_color_choices = PropertyMock(
                return_value=BootstrapColorChoices
            )

            field.field_config = mock_field_config

            choices = field.get_choices()

            # With custom_first layout, custom choices should appear first
            assert isinstance(choices, list)
            assert len(choices) > 1
            # Find the custom choice and verify it appears before bootstrap
            custom_choice_index = next(
                i
                for i, choice in enumerate(choices)
                if choice[0] == "bg-field"
            )
            bootstrap_choice_index = next(
                i
                for i, choice in enumerate(choices)
                if choice[0].startswith("bg-primary")
            )
            assert custom_choice_index < bootstrap_choice_index, (
                "Custom choices should appear before default choices with custom_first layout"  # noqa: E501
            )


class TestSortedChoices:
    """Tests for the sorted_choices function."""

    def test_sorted_choices_by_label(self) -> None:
        """Test sorted_choices function."""
        choices = [
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
        ]
        sort_by = "label"
        sorted_choices = sort_choices(choices, sort_by)
        assert sorted_choices == [
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
            ("bg-red", "Red"),
        ]

    def test_sorted_choices_empty(self) -> None:
        """Test sorted_choices with empty list."""
        choices = []
        sort_by = "label"
        sorted_choices = sort_choices(choices, sort_by)
        assert sorted_choices == []

    def test_sorted_choices_no_sort_by(self) -> None:
        """Test sorted_choices without sort_by."""
        choices = [
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
        ]
        sort_by = None
        sorted_choices = sort_choices(choices, sort_by)
        assert sorted_choices == choices

    def test_sorted_choices_invalid_sort_by(self) -> None:
        """Test sorted_choices with invalid sort_by."""
        choices = [
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
        ]
        sort_by = "invalid"
        sorted_choices = sort_choices(choices, sort_by)
        assert sorted_choices == choices

    def test_sorted_choices_by_value(self) -> None:
        """Test sorted_choices by value."""
        choices = [
            ("bg-red", "Red"),
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
        ]
        sort_by = "value"
        sorted_choices = sort_choices(choices, sort_by)
        assert sorted_choices == [
            ("bg-blue", "Blue"),
            ("bg-green", "Green"),
            ("bg-red", "Red"),
        ]
