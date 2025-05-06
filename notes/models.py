import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Task(pk={self.pk})," \
               f"user=({self.user})," \
               f"title=({self.title})," \
               f"created_at=({self.created_at})," \
               f"updated_at=({self.updated_at})," \
               f"is_completed={self.is_completed}"


class CompleteTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"CompleteTask(pk={self.pk}," \
               f"user=({self.user})," \
               f"title=({self.title})," \
               f"created_at=({self.created_at})," \
               f"updated_at=({self.updated_at})," \
               f"completed_at=({self.completed_at})," \
               f"is_completed=({self.is_completed})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"token=({self.token})," \
               f"user=({self.user.username})," \
               f"created_at=({self.created_at})"


class HeaderTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    header_title = models.CharField(max_length=15)

    def __str__(self):
        return f"header-title(pk={self.pk})," \
               f"user={self.user.username}," \
               f"header-title={self.header_title}"
