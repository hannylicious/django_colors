from django import forms


class ColorChoiceWidget(forms.Select):
    template_name = "color_select.html"
    option_template_name = "color_select_option.html"

    def __init__(self, attrs=None, choices=None):
        super().__init__(attrs, choices)
