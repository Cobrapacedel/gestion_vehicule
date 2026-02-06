from django.db import models
from django.db.models import Q


class ContractQuerySet(models.QuerySet):

    def visible_for(self, user):
        """
        Un contrat est visible uniquement par :
        - old_user
        - new_user
        - employés de old_user
        """

        return self.filter(
            Q(old_user=user) |
            Q(new_user=user) |
            Q(old_user__businessprofile__employees__user=user)
        ).distinct()

    # --------------------
    # Helpers (facultatifs)
    # --------------------
    def sells(self):
        return self.filter(contract_type="sell")

    def rents(self):
        return self.filter(contract_type="rent")

    def loans(self):
        return self.filter(contract_type="loan")

    def services(self):
        return self.filter(contract_type="service")