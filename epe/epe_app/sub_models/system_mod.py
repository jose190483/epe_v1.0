from django.db import models
class system_Info(models.Model):
    system_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["system_name"]

    def __str__(self):
        return self.system_name

class system_short_Info(models.Model):
    ss_system_name = models.ForeignKey(system_Info,on_delete=models.CASCADE)
    ss_system_short_name = models.CharField(max_length=100)

    def __str__(self):
        return self.ss_system_short_name

