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
        ]
    )


class PalasForm(forms.Form):
    pages = forms.IntegerField(
        label='Ingrese un número entero entre 1 y 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'number'}),
    )
    theme = forms.ChoiceField(
        choices=[
            ("Narrativa contemporanea", "Narrativa contemporanea"),
            ("Narrativa clasica", "Narrativa clasica"),
            ("Biografias, memorias","Biografias y memorias"),
            ("Clasicos grecolatinos","Clasicos grecolatinos"),
            ("Infantil","Infantil"),
            ("Psicologia","Psicologia"),
            ("Educacion","Educacion"),
            ("Pintura, arquitectura","Pintura y arquitectura"),
            ("Cine, fotografia, musica, flamenco","Cine, fotografia, musica, flamenco"),
            ("Viajes","Viajes"),
            ("Turismo, mapas","Turismo, mapas"),
            ("Naturaleza, animales, plantas, senderismo","Naturaleza, animales, plantas, senderismo"),
            ("Caza, deporte, tauromaquia","Caza, deporte, tauromaquia"),
            ("Cocina, alimentacion, salud","Cocina, alimentacion, salud"),
            ("Historia de España","Historia de España"),
            ("Historia universal","Historia universal"),
            ("Geografia","Geografia"),
            ("Filosofia","Filosofia"),
            ("Sociologia","Sociologia"),
            ("Ciencia, divulgacion cientifica","Ciencia, divulgacion cientifica"),
            ("Religiones, espiritualidad, mitologia","Religiones, espiritualidad, mitologia"),
            ("Linguistica, teoria literaria, historia de la literatura","Linguistica, teoria literaria, historia de la literatura"),
            ("Narrativa ingles","Narrativa ingles"),
            ("Narrativa portugues","Narrativa portugues"),
            ("Narrativa italiano","Narrativa italiano"),
            ("Narrativa aleman","Narrativa aleman"),
            ("Narrativa frances","Narrativa frances"),
            ("Poesia","Poesia"),
            ("Teatro","Teatro"),
            ("Ajedrez, juegos","Ajedrez, juegos"),
            ("Manualidades, decoracion","Manualidades, decoracion"),
            ("Atlas geograficos","Atlas geograficos"),
            ("Atlas historicos","Atlas historicos"),
            ("Juvenil","Juvenil"),
            ("Sevilla, Andalucia","Sevilla, Andalucia"),
            ("Ilustrados, comics","Ilustrados, comics"),
            ("Manga","Manga"),
            ("Arte","Arte")
        ]
    )
