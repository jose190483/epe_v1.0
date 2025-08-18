from django.db import models
from ..models import status_Info,MyUser,datatype_Info,dictionary_Info,unit_type_info

class prameter_definition_info(models.Model):
    pd_id = models.CharField(max_length=100, blank=True,null=True, default='')
    pd_name = models.CharField(max_length=100, null=True, default='')
    pd_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    pd_library =models.ForeignKey(dictionary_Info,on_delete=models.CASCADE,default=1)
    pd_status =models.ForeignKey(status_Info,on_delete=models.CASCADE,default=1)
    pd_datatype=models.ForeignKey(datatype_Info,on_delete=models.CASCADE,default=1)
    pd_description = models.TextField(max_length=500, default='')
    pd_updated_at = models.DateTimeField(null=True, auto_now=True)
    pd_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,
                                            related_name='pd_updated_by', db_column='pd_updated_by')

    def __str__(self):
        return self.pd_name

    class Meta:
        ordering = ["-pd_id"]