from django.db import models
class datatype_Info(models.Model):
    dt_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["dt_name"]

    def __str__(self):
        return self.dt_name