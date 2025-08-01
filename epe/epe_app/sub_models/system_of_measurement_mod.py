from django.db import models

class system_of_measurement_info(models.Model):
    som_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.som_name

    class Meta:
        ordering = ["som_name"]