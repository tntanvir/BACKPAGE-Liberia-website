from django.db import models

# Create your models here.


class Ads(models.Model):
    class Page(models.TextChoices):
        HOME = 'home', 'Home'
        VIDEO = 'video', 'Video'
        MUSIC = 'music', 'Music'
        MARKET = 'market', 'Market'

    page = models.CharField(max_length=20, choices=Page.choices, default=Page.HOME)
    image = models.ImageField(upload_to='ads/')
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.page
