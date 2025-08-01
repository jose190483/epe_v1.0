from django.db import models
from ..models import unit_type_info,system_of_measurement_info
class uom_info(models.Model):
    uom_unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    uom_symbol = models.CharField(max_length=100, default='')
    uom_system_of_measurement=models.ForeignKey(system_of_measurement_info,on_delete=models.CASCADE,default=1)


    def __str__(self):
        return str(self.uom_symbol)

    class Meta:
        ordering = ["uom_symbol"]