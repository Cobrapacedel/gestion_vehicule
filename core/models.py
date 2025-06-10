from django.db import models
from django.conf import settings

class ProjectInfo(models.Model):
    name = models.CharField(max_length=255, default="Jere Machin")
    creation_date = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    last_change = models.DateField(null=True, blank=True)

    version = models.CharField(max_length=50, default="Beta")
    developer = models.CharField(max_length=100, default="Cobrapacedel™")
    contact_email = models.EmailField(default="delinoiskadhaffimacarthur@gmail.com")

    class Meta:
        verbose_name = "Project Information"
        verbose_name_plural = "Project Information"

    def __str__(self):
        return f"{self.name} v{self.version}"