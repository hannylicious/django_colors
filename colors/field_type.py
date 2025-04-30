"""FieldType Enum."""

from enum import Enum


class FieldType(Enum):
    """Enumeration for specifying the CSS property type for color fields.

    Attributes:
        BACKGROUND: Use background CSS property
        TEXT: Use text CSS property

    """

    BACKGROUND = "background_css"
    TEXT = "text_css"
