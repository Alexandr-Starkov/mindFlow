import uuid

from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Task(pk={self.pk}), user={self.user}, title={self.title}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Token: {self.token} for User: {self.user.username} Created At: {self.created_at}'


class HeaderTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    header_title = models.CharField(max_length=15)

    def __str__(self):
        return f'Header-Title(pk={self.pk}), User: {self.user.username}, Header-Title: {self.header_title}'
