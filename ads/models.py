from django.db import models

# Create your models here.
class AdsPage(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Ads(models.Model):

    page = models.ForeignKey(AdsPage, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='ads/')
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.page.name if self.page else "No Page"
