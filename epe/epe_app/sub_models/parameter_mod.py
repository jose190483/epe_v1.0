from django.db import models
from ..models import datatype_Info,equipment_shortInfo,equipmentInfo,system_short_Info,system_of_measurement_info,dictionary_Info,component_Info,system_Info,project_info,unit_type_info,prameter_definition_info,uom_info,parameter_definition_lov_info

class prameter_info(models.Model):
    p_id = models.CharField(max_length=100, blank=True,null=True, default='')
    p_name = models.CharField(max_length=100, null=True, default='')
    p_name_as_is = models.CharField(max_length=100, null=True, default='')
    p_uom=models.ForeignKey(uom_info,on_delete=models.CASCADE,default=1)
    p_definition=models.ForeignKey(prameter_definition_info,on_delete=models.PROTECT,default=1)
    # p_project=models.ForeignKey(project_info,on_delete=models.CASCADE,default=1)
    p_system=models.ForeignKey(system_Info,on_delete=models.PROTECT,default=1)
    p_system_short=models.ForeignKey(system_short_Info,on_delete=models.PROTECT,null=True,blank=True)
    p_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    # p_parameter_dictionary=models.ForeignKey(dictionary_Info,on_delete=models.CASCADE,default=1)
    p_parameter_lov=models.ForeignKey(parameter_definition_lov_info,on_delete=models.CASCADE,blank=True,null=True)
    p_parameter_unit_measurement = models.ForeignKey(system_of_measurement_info, on_delete=models.CASCADE, blank=True, null=True,default=1)
    p_value= models.FloatField(default=0.0,blank=True,null=True)
    p_equipment_name=models.ForeignKey(equipmentInfo,on_delete=models.PROTECT)
    p_equipment_short=models.ForeignKey(equipment_shortInfo,on_delete=models.PROTECT)
    p_parameter_def_data_type=models.ForeignKey(datatype_Info,on_delete=models.PROTECT,null=True,blank=True)

    def __str__(self):
        return self.p_id

    class Meta:
        ordering = ["-p_id"]