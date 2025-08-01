from django.db import models
from ..models import dictionary_Info,component_Info,system_Info,project_info,unit_type_info,prameter_definition_info,uom_info

class prameter_info(models.Model):
    p_id = models.CharField(max_length=100, blank=True,null=True, default='')
    p_name = models.CharField(max_length=100, null=True, default='')
    p_uom=models.ForeignKey(uom_info,on_delete=models.CASCADE,default=1)
    p_definition=models.ForeignKey(prameter_definition_info,on_delete=models.CASCADE,default=1)
    p_project=models.ForeignKey(project_info,on_delete=models.CASCADE,default=1)
    p_system=models.ForeignKey(system_Info,on_delete=models.CASCADE,default=1)
    p_component=models.ForeignKey(component_Info,on_delete=models.CASCADE,default=1)
    p_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    p_parameter_dictionary=models.ForeignKey(dictionary_Info,on_delete=models.CASCADE,default=1)
    p_value= models.FloatField(default=0.0)



    def __str__(self):
        return self.p_id

    class Meta:
        ordering = ["-p_id"]