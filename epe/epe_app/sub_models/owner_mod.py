from django.db import models
class owner_info(models.Model):
    owner_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["owner_name"]

    def __str__(self):
        return self.owner_name