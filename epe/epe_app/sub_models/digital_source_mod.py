from django.db import models
class digital_source_info(models.Model):
    ds_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["ds_name"]

    def __str__(self):
        return self.ds_name