from django.db import models

class PDFChunks(models.Model):
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    chunks = models.JSONField()
    embeddings = models.JSONField(default=list)  # Default to an empty list
    uploaded_at = models.DateTimeField(auto_now_add=True)