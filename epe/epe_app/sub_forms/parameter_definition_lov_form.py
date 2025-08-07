from django import forms
from ..models import parameter_definition_lov_info

class parameter_definition_lov_form(forms.ModelForm):
    class Meta:
        model = parameter_definition_lov_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(parameter_definition_lov_form,self).__init__(*args, **kwargs)
        self.fields['pdl_parameter_definition'].empty_label = "--Select--"
