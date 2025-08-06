from django.db import models
class dictionary_Info(models.Model):
    dictionary_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["dictionary_name"]

    def __str__(self):
        return self.dictionary_name