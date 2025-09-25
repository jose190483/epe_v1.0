from django.db import models
from ..models import MyUser,status_Info,owner_info,digital_source_info,equipment_shortInfo,equipmentInfo,system_short_Info,system_of_measurement_info,system_Info,unit_type_info,prameter_definition_info,uom_info,parameter_definition_lov_info

class prameter_info(models.Model):
    p_id = models.CharField(max_length=100, blank=True,null=True, default='')
    p_name = models.CharField(max_length=100, null=True, default='')
    p_name_as_is = models.CharField(max_length=100,null=True, default='')
    p_uom=models.ForeignKey(uom_info,on_delete=models.CASCADE)
    p_definition=models.ForeignKey(prameter_definition_info,on_delete=models.PROTECT)
    # p_project=models.ForeignKey(project_info,on_delete=models.CASCADE,default=1)
    p_system=models.ForeignKey(system_Info,on_delete=models.PROTECT)
    p_system_short=models.ForeignKey(system_short_Info,on_delete=models.PROTECT,null=True,blank=True)
    p_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE)
    # p_parameter_dictionary=models.ForeignKey(dictionary_Info,on_delete=models.CASCADE,default=1)
    p_parameter_lov=models.ForeignKey(parameter_definition_lov_info,on_delete=models.CASCADE,blank=True,null=True)
    p_value= models.FloatField(default=0.0,blank=True,null=True)
    p_equipment_name=models.ForeignKey(equipmentInfo,on_delete=models.PROTECT,null=True,blank=True)
    p_equipment_short=models.ForeignKey(equipment_shortInfo,on_delete=models.PROTECT,null=True,blank=True)
    p_status=models.ForeignKey(status_Info,on_delete=models.PROTECT,null=True,blank=True,default=1)
    p_parameter_name_combo=models.CharField(max_length=150,null=True,blank=True)
    p_digital_source = models.ManyToManyField(digital_source_info,blank=True,null=True)
    p_owner = models.ManyToManyField(owner_info, blank=True,null=True)
    p_updated_at = models.DateTimeField(null=True, auto_now=True)
    p_updated_by = models.ForeignKey(MyUser, on_delete=models.PROTECT, null=True,
                                            related_name='p_updated_by', db_column='p_updated_by')
    p_parameter_prefix = models.CharField(max_length=150, null=True, blank=True)
    p_parameter_suffix = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return str(self.p_id) if self.p_id is not None else ""

    class Meta:
        ordering = ["-p_id"]