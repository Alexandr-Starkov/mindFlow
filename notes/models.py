from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Task(pk={self.pk}), title={self.title}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Token for {self.user.username}'


class HeaderTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    header_title = models.CharField(max_length=15)

    def __str__(self):
        return f'Header-Title(pk={self.pk}), User: {self.user.username}, Header-Title: {self.header_title}'

