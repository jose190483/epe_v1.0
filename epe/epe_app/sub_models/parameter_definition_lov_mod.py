from django.db import models
from ..models import prameter_definition_info,system_of_measurement_info
class parameter_definition_lov_info(models.Model):
    pdl_parameter_definition=models.ForeignKey(prameter_definition_info,on_delete=models.CASCADE,blank=True,null=True)
    pdl_lov = models.CharField(max_length=200, default='')

    def __str__(self):
        return str(self.pdl_lov)

    class Meta:
        ordering = ["pdl_lov"]