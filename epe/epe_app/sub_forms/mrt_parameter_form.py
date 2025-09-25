from django import forms
from ..models import mrt_prameter_info

class mrt_parameter_form(forms.ModelForm):
    class Meta:
        model = mrt_prameter_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(mrt_parameter_form,self).__init__(*args, **kwargs)
        self.fields['mrt_parameter_ref'].empty_label = "--Select--"
        self.fields['mrt_status'].empty_label = "--Select--"

