from .models import Documents, Keywords
from django import forms
class LinkForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['link']
