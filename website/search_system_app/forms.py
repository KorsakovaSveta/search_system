from .models import Documents, Keywords
from django import forms
class LinkForm(forms.ModelForm):
    link = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Input link...'}), label='')
    class Meta:
        model = Documents
        fields = ['link']
    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs.update({'class': 'input_link'})