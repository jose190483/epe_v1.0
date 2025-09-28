from django.db import models

class PDFChunks(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    file_hash = models.CharField(max_length=64, unique=True)  # content-based uniqueness
    chunks = models.JSONField()  # list[str]
    embeddings = models.JSONField()  # list[list[float]] (MiniLM: 384 dim)
    kv_index = models.JSONField(null=True, blank=True)  # optional extracted key-values
    num_chunks = models.IntegerField(default=0)
    dim = models.IntegerField(default=384)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
