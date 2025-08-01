from django.db import models
class system_Info(models.Model):
    system_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["system_name"]

    def __str__(self):
        return self.system_name