from django import forms
from ..models import parameter_definition_lov_info

class ParameterDefinitionLovForm(forms.ModelForm):
    class Meta:
        model = parameter_definition_lov_info
        # fields = ['pdl_lov']
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.parameter = kwargs.pop('parameter', None)
        super().__init__(*args, **kwargs)

    def clean_pdl_lov(self):
        lov_value = self.cleaned_data['pdl_lov']
        if parameter_definition_lov_info.objects.filter(
                pdl_parameter_definition=self.parameter,
                pdl_lov__iexact=lov_value).exists():
            raise forms.ValidationError("This value already exists for this parameter.")
        return lov_value
