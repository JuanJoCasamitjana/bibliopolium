from django import forms

class PagesForm(forms.Form):
    pages = forms.IntegerField(
        label='Ingrese un número entero entre 1 y 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'number'}),
    )

class TroaForm(forms.Form):
    pages = forms.IntegerField(
        label='Ingrese un número entero entre 1 y 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'number'}),
    )
    theme = forms.ChoiceField(choices=[("narrativa","Narrativa"),
    ("familia","Familia"),
    ("economia-y-empresa","Economia-y-empresa"),
    ("espiritualidad","Espiritualidad"),
    ("biografias","Biografias"),
    ("historia","Historia"),
    ("infantil","Infantil"),
    ("juvenil","Juvenil")])

class BoticaForm(forms.Form):
    pages = forms.IntegerField(
        label='Ingrese un número entero entre 1 y 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'number'}),
    )
    theme = forms.ChoiceField(
        choices=[
            ("01", "Infantil y juvenil"),
            ("02", "Artes"),
            ("03", "Humanidades"),
            ("04", "Ciencias y tecnología"),
            ("05", "Derecho y empresa"),
            ("06", "Narrativa y ficcion"),
            ("07", "Hogar y estilo de vida"),
            ("08", "Desarrollo personal"),
            ("09", "Viajes y guias"),
            ("10", "Temas andaluces y locales")
        ], required=False
    )
