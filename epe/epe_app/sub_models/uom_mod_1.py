from django.db import models
from ..models import unit_type_info,system_of_measurement_info
class uom_info_1(models.Model):
    unit_type=models.ForeignKey(unit_type_info,on_delete=models.CASCADE,default=1)
    symbol = models.CharField(max_length=100, default='')
    system_of_measurement=models.ForeignKey(system_of_measurement_info,on_delete=models.CASCADE,default=1)


    def __str__(self):
        return str(self.symbol)

    class Meta:
        ordering = ["symbol"]