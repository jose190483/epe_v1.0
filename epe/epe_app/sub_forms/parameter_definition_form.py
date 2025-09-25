from django import forms
from ..models import prameter_definition_info,digital_source_info

class parameter_definition_form(forms.ModelForm):
    class Meta:
        model = prameter_definition_info
        fields = '__all__'

    def clean_pd_name(self):
        pd_name = self.cleaned_data.get('pd_name')
        if prameter_definition_info.objects.filter(pd_name=pd_name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This name already exists. Please choose a different one.")
        return pd_name

    def __init__(self, *args, **kwargs):
        super(parameter_definition_form,self).__init__(*args, **kwargs)
        self.fields['pd_unit_type'].empty_label = "--Select--"
        self.fields['pd_library'].empty_label = "--Select--"
        self.fields['pd_datatype'].empty_label = "--Select--"
        self.fields['pd_status'].empty_label = "--Select--"