from django.db import models

class Scene(models.Model):
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="scenes",
    )
    
    title = models.CharField(max_length=200)
    goal = models.TextField()
    
    def __str__(self):
        return self.title