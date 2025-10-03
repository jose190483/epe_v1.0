from django.db import models
from ..models import system_Info
class equipmentInfo(models.Model):
    equipment_system_name = models.ForeignKey(system_Info,on_delete=models.PROTECT)
    equipment_name = models.CharField(max_length=100, null=True,default='')
    equipment_name_short = models.CharField(max_length=100, null=True,default='')
    class Meta:
        ordering = ["equipment_name"]

    def __str__(self):
        return self.equipment_name or ""

class equipment_shortInfo(models.Model):
    es_equipment_name = models.ForeignKey(equipmentInfo,on_delete=models.PROTECT)
    es_equipment_short_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["es_equipment_short_name"]

    def __str__(self):
        return self.es_equipment_short_name or ""