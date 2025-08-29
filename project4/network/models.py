from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    def __str__(self):
        return self.username


class Post(models.Model):
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."

    def like_count(self):
        return self.likes.count()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
