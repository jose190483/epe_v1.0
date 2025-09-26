from django.db import models

class PDFChunks(models.Model):
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    chunks = models.JSONField(default=list)  # Default to an empty list
    embeddings = models.JSONField(default=list)  # Default to an empty list
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['uploaded_at']),  # Add an index for uploaded_at
        ]

    def clean(self):
        # Ensure chunks and embeddings are lists
        if not isinstance(self.chunks, list):
            raise ValueError("Chunks must be a list.")
        if not isinstance(self.embeddings, list):
            raise ValueError("Embeddings must be a list.")