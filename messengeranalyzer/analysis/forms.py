from django import forms
from data_handler.models import Contact
from .enums import GeneralAnalysisType, ContactAnalysisType

class GeneralAnalysisForm(forms.Form):
    analysis_type = forms.ChoiceField(choices=[(analysis_type, analysis_type.value) for analysis_type in (GeneralAnalysisType)], label="Select an analysis")

class ContactAnalysisForm(forms.Form):
    selected_contact = forms.ModelChoiceField(queryset=Contact.objects.all(), label='Select a contact')
    analysis_type = forms.ChoiceField(choices=[(analysis_type, analysis_type.value) for analysis_type in (ContactAnalysisType)], label="Select an analysis")