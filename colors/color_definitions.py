from django.db.models import TextChoices


class ColorChoices(TextChoices):
    BLUE = "blue", "Blue"
    GREEN = "green", "Green"
    YELLOW = "yellow", "Yellow"
    RED = "red", "Red"
    PURPLE = "purple", "Purple"
    INDIGO = "indigo", "Indigo"
    PINK = "pink", "Pink"
    ORANGE = "orange", "Orange"
    TEAL = "teal", "Teal"
    CYAN = "cyan", "Cyan"
    GRAY = "gray", "Gray"

    @property
    def bg_css_class(self):
        return ""

    @property
    def text_css_class(self):
        return ""

    @classmethod
    def choices_list(cls):
        options = [
            (member.value, member.label, member.bg_css_class, member.text_css_class)
            for member in cls
        ]
        return options


class BootstrapColorChoices(TextChoices):
    BLUE = "blue", "Blue"
    GREEN = "green", "Green"
    YELLOW = "yellow", "Yellow"
    RED = "red", "Red"
    PURPLE = "purple", "Purple"
    INDIGO = "indigo", "Indigo"
    PINK = "pink", "Pink"
    ORANGE = "orange", "Orange"
    TEAL = "teal", "Teal"
    CYAN = "cyan", "Cyan"
    GRAY = "gray", "Gray"

    @property
    def bg_css_class(self):
        bg_classes = {
            "blue": "bg-primary-200",
            "green": "bg-success-200",
            "yellow": "bg-warning-200",
            "red": "bg-danger-200",
            "purple": "bg-purple-200",
            "indigo": "bg-indigo-200",
            "pink": "bg-pink-200",
            "orange": "bg-orange-200",
            "teal": "bg-teal-200",
            "cyan": "bg-cyan-200",
            "gray": "bg-gray-200",
        }
        return bg_classes.get(self.value, "")

    @property
    def text_css_class(self):
        text_classes = {
            "blue": "text-primary",
            "green": "text-success",
            "yellow": "text-warning",
            "red": "text-danger",
            "purple": "text-purple",
            "indigo": "text-indigo",
            "pink": "text-pink",
            "orange": "text-orange",
            "teal": "text-teal",
            "cyan": "text-cyan",
            "gray": "text-gray",
        }
        return text_classes.get(self.value, "")

    @classmethod
    def choices_list(cls):
        options = [
            (member.value, member.label, member.bg_css_class, member.text_css_class)
            for member in cls
        ]
        return options
