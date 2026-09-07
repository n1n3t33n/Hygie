from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """
    Modèle d'authentification unique (AUTH_USER_MODEL).
    Porte uniquement la connexion et les permissions.
    Les données métier (Client, Agent) viendront dans des profils
    liés en OneToOne — prochaine étape, une fois la question Tarif tranchée
    et le mapping entités/apps confirmé.
    """
    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.get_full_name() or self.username