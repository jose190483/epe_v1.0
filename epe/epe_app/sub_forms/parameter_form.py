from django import forms
from ..models import prameter_info,system_Info,system_short_Info

class parameter_form(forms.ModelForm):
    class Meta:
        model = prameter_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(parameter_form,self).__init__(*args, **kwargs)
        self.fields['p_uom'].empty_label = "--Select--"
        self.fields['p_parameter_unit_measurement'].empty_label = "--Select--"
        self.fields['p_parameter_lov'].empty_label = "--Select--"
        self.fields['p_equipment_name'].empty_label = "--Select--"
        self.fields['p_equipment_short'].empty_label = "--Select--"
        self.fields['p_system'].empty_label = "--Select--"
        self.fields['p_system_short'].empty_label = "--Select--"
        self.fields['p_system_short'].empty_label = "--Select--"
        self.fields['p_definition'].empty_label = "--Select--"

