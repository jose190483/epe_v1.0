from django.db import models
from django.db.models import Q

class PDFChunks(models.Model):
    file_name  = models.CharField(max_length=255)
    file_hash  = models.CharField(max_length=64, null=True, blank=True, default=None, db_index=True)
    chunks     = models.JSONField(default=list)
    embeddings = models.JSONField(default=list)
    num_chunks = models.IntegerField(default=0)
    dim        = models.IntegerField(default=384)

    class Meta:
        constraints = [
            # unique ONLY when file_hash is NOT NULL
            models.UniqueConstraint(fields=["file_hash"], condition=Q(file_hash__isnull=False),
                                    name="uniq_pdfchunks_file_hash_when_present"),
        ]
