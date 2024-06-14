from django.forms import Form, CharField, Textarea, ChoiceField


ENCODING_CHOICES = [
    ('utf-8', 'UTF-8'),
    ('utf-16le', 'UTF-16LE'),
    ('utf-16be', 'UTF-16BE'),
    ('iso-8859-1', 'ISO-8859-1'),
    ('iso-8859-15', 'ISO-8859-15'),
    ('windows-1251', 'Windows-1251'),
]


class DecodeTextForm(Form):
    text = CharField(widget=Textarea)
    in_encoding = ChoiceField(required=False, choices=ENCODING_CHOICES)
    out_encoding = ChoiceField(required=False, choices=ENCODING_CHOICES)
