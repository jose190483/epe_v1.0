from django.db import models
class status_Info(models.Model):
    status_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["status_name"]

    def __str__(self):
        return self.status_name