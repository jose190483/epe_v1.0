from django.db import models
class component_Info(models.Model):
    component_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["component_name"]

    def __str__(self):
        return self.component_name