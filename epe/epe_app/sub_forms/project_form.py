from django import forms
from ..models import project_info

class project_form(forms.ModelForm):
    class Meta:
        model = project_info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(project_form,self).__init__(*args, **kwargs)
        # self.fields['p_uom'].empty_label = "--Select--"
