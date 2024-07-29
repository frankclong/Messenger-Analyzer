from django import forms
from data_handler.models import Contact
from .enums import GeneralAnalysisType, ContactAnalysisType

class GeneralAnalysisForm(forms.Form):
    analysis_type = forms.ChoiceField(choices=[(analysis_type.name, analysis_type.value) for analysis_type in (GeneralAnalysisType)], label="Select an analysis")

class ContactAnalysisForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['selected_contact'].queryset = Contact.objects.filter(user=user)

    selected_contact = forms.ModelChoiceField(queryset=None, label='Select a contact')
    analysis_type = forms.ChoiceField(choices=[(analysis_type.name, analysis_type.value) for analysis_type in (ContactAnalysisType)], label="Select an analysis")