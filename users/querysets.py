from django.db import models


class ClientQuerySet(models.QuerySet):

    def visible_for(self, user):
        return self.filter(owner=user)
        
class EmployeeQuerySet(models.QuerySet):
    def visible_for(self, user):
        if user.role in ["dealer", "agency", "garage"]:
            return self.filter(business__user=user)
        return self.none()