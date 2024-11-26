from django.contrib.auth.models import AbstractUser
from django.db import models

class UtilisateurPersonnalise(AbstractUser):
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    numero_telephone = models.CharField(max_length=15, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
