from django.db import models
from .querysets import ClientQuerySet, EmployeeQuerySet

class ClientManager(models.Manager):
    def get_queryset(self):
        return ClientQuerySet(self.model, using=self._db)

    def visible_for(self, user):
        return self.get_queryset().visible_for(user)
        
class EmployeeManager(models.Manager):
    def get_queryset(self):
        return EmployeeQuerySet(self.model, using=self._db)

    def visible_for(self, user):
        return self.get_queryset().visible_for(user)