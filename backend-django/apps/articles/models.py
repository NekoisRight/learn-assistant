from django.db import models

class Article(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    level = models.CharField(max_length=20, default="B1")
    source = models.CharField(max_length=200, default="user_upload")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title