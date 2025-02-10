from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Task(pk={self.pk}), title={self.title}"
