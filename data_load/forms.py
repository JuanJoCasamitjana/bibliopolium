from django import forms
from .models import Category


class LoadOfTagForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Select a category to index all of its books',
        widget=forms.Select(
            attrs={
                'class':'form-select'
            }
        )
        )
    def __init__(self, *args, **kwargs):
        super(LoadOfTagForm, self).__init__(*args, **kwargs)
        self.fields['tag'].label = 'Select a category to index all of its books'  # Modificar el texto del label
        self.fields['tag'].label_suffix = ''  # Eliminar el sufijo del label (por ejemplo, ":")
        self.fields['tag'].widget.attrs.update({'class': 'form-label'})

class LoadReviewersForm(forms.Form):
    choice = forms.ChoiceField(
        choices=[
            ('All','All'),
            ('Unchecked','Unchecked')
        ],
        widget=forms.Select(
            attrs={
                'class':'form-select'
            }
        )
    )
    def __init__(self, *args, **kwargs):
        super(LoadReviewersForm, self).__init__(*args, **kwargs)
        self.fields['choice'].label = 'Select an option'  # Modificar el texto del label
        self.fields['choice'].label_suffix = ''  # Eliminar el sufijo del label (por ejemplo, ":")
        self.fields['choice'].widget.attrs.update({'class': 'form-label'})

class LoadReviewsForm(forms.Form):
    amount = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-input'
            }
        )
    )
    def __init__(self, *args, **kwargs):
        super(LoadReviewsForm, self).__init__(*args, **kwargs)
        self.fields['amount'].label = 'How much to scrape'  # Modificar el texto del label
        self.fields['amount'].label_suffix = ''  # Eliminar el sufijo del label (por ejemplo, ":")
        self.fields['amount'].widget.attrs.update({'class': 'form-label'})


class LoadBookTagsForm(forms.Form):
    amount = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-input'
            }
        )
    )
    def __init__(self, *args, **kwargs):
        super(LoadBookTagsForm, self).__init__(*args, **kwargs)
        self.fields['amount'].label = 'How much to scrape'  # Modificar el texto del label
        self.fields['amount'].label_suffix = ''  # Eliminar el sufijo del label (por ejemplo, ":")
        self.fields['amount'].widget.attrs.update({'class': 'form-label'})