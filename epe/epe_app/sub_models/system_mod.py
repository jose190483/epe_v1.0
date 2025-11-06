from django.db import models
class system_Info(models.Model):
    system_name = models.CharField(max_length=100, null=True,default='')
    system_name_short = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["system_name"]

    def __str__(self):
        return str(self.system_name) if self.system_name is not None else ""

class system_short_Info(models.Model):
    ss_system_name = models.ForeignKey(system_Info,on_delete=models.CASCADE)
    ss_system_short_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.ss_system_short_name) if self.ss_system_short_name is not None else ""

