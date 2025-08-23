from django import forms
from ..models import prameter_definition_info,digital_source_info

class parameter_definition_form(forms.ModelForm):
    class Meta:
        model = prameter_definition_info
        fields = '__all__'
        error_messages = {
            'pd_name': {
                'unique': "This name already exists. Please choose a different one.",
            }
        }

    def __init__(self, *args, **kwargs):
        super(parameter_definition_form,self).__init__(*args, **kwargs)
        self.fields['pd_unit_type'].empty_label = "--Select--"
        self.fields['pd_library'].empty_label = "--Select--"
        self.fields['pd_datatype'].empty_label = "--Select--"
        self.fields['pd_status'].empty_label = "--Select--"