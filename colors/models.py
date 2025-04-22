from django.db.models import Model
from django.db.models.fields import CharField


class ColorModel(Model):
    name = CharField(max_length=100)
    background_css = CharField(max_length=200)
    text_css = CharField(max_length=200)

    class Meta:
        abstract = True

