from django import forms
from ..models import prameter_definition_info,digital_source_info

class parameter_definition_form(forms.ModelForm):
    pd_digital_source = forms.ModelMultipleChoiceField(
        queryset=digital_source_info.objects.all(),
        widget=forms.SelectMultiple,
        required=False
    )
    class Meta:
        model = prameter_definition_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(parameter_definition_form,self).__init__(*args, **kwargs)
        self.fields['pd_unit_type'].empty_label = "--Select--"
        self.fields['pd_library'].empty_label = "--Select--"
        self.fields['pd_digital_source'].empty_label = "--Select--"
        self.fields['pd_owner'].empty_label = "--Select--"
        self.fields['pd_datatype'].empty_label = "--Select--"