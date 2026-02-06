from django.core.management.base import BaseCommand
from users.models import Profile
from django.db import transaction

class Command(BaseCommand):
    help = "Nettoie les doublons de profils (garde le premier profil par utilisateur)."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        seen_users = set()
        deleted_count = 0

        for profile in Profile.objects.all().order_by("id"):
            if profile.user_id in seen_users:
                self.stdout.write(f"Suppression du profil en doublon: {profile.id} (user_id={profile.user_id})")
                profile.delete()
                deleted_count += 1
            else:
                seen_users.add(profile.user_id)

        self.stdout.write(self.style.SUCCESS(f"✅ Nettoyage terminé. {deleted_count} doublons supprimés."))