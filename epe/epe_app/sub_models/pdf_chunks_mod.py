from django.db import models


class PDFChunks(models.Model):
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    chunks = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)