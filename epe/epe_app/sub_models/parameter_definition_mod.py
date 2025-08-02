from django.db import models
from ..models import datatype_Info,owner_info,digital_source_info,dictionary_Info,unit_type_info

class prameter_definition_info(models.Model):
    pd_id = models.CharField(max_length=100, blank=True,null=True, default='')
    pd_name = models.CharField(max_length=100, null=True, default='')
    pd_digital_source = models.ManyToManyField(digital_source_info)
    pd_owner=models.ForeignKey(owner_info,on_delete=models.CASCADE,default=1)
    pd_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    pd_library =models.ForeignKey(dictionary_Info,on_delete=models.CASCADE,default=1)
    pd_datatype=models.ForeignKey(datatype_Info,on_delete=models.CASCADE,default=1)
    pd_description = models.TextField(max_length=500, default='')

    def __str__(self):
        return self.pd_name

    class Meta:
        ordering = ["-pd_id"]