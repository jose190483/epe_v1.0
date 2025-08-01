from django.db import models

class unit_type_info(models.Model):
    ut_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.ut_name

    class Meta:
        ordering = ["ut_name"]