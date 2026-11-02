from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField("Encadrant actif", default=True)

    def __str__(self):
        return (f'Staff member: {self.user.first_name} {self.user.last_name}')

class Rider(models.Model):

    FFC_CATEGORIES = [
        ("ELITE", "Élite"),
        ("OPEN_1", "Open 1"),
        ("OPEN_2", "Open 2"),
        ("OPEN_3", "Open 3"),
        ("ACCESS_1", "Access 1"),
        ("ACCESS_2", "Access 2"),
        ("ACCESS_3", "Access 3"),
        ("ACCESS_4", "Access 4"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category_ffc = models.CharField(
        "Catégorie FFC",
        max_length=20,
        choices=FFC_CATEGORIES,
        default="OPEN_1",
    )

    belong_to_dn = models.BooleanField("Coureur DN", default=False)
    is_active = models.BooleanField("Coureur actif", default=True)

    def __str__(self):
        if self.is_active:
            active = "Actif"
        else:
            active = "Archivé"

        return (
            f"[{self.user.first_name} {self.user.last_name}] {self.category_ffc} ({active})"
        )


class Race(models.Model):
    # Les choix pour le type d'épreuve
    CATEGORY_CHOICES = [
        ("elite_nationale", "ELITE NATIONALE"),
        ("elite_regionale", "ELITE REGIONALE"),
        ("open1", "OPEN 1"),
    ]

    title = models.CharField("Nom de la course", max_length=150)
    date = models.DateField("Date de la course")
    location = models.CharField("Lieu / Ville", max_length=100)
    category_type = models.CharField(
        "Type d'épreuve",
        max_length=100,
        choices=CATEGORY_CHOICES,
        default="elite_regionale",
    )
    is_dn_race = models.BooleanField("Deplacement DN")
    created_at = models.DateTimeField(auto_now_add=True)
    riders = models.ManyToManyField(Rider, blank=True, related_name="races")
    staff_members = models.ManyToManyField(Staff, blank=True, related_name='races')
    results_entered = models.BooleanField(default=False, help_text="Indique si les résultats de la course ont été saisis")

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"[{self.category_type}] {self.title} ({self.date})"

    @property
    def active_riders(self):
        """Renvoie directement la liste des coureurs actifs pour cette course"""
        return Rider.objects.filter(is_active=True)


class RacePresence(models.Model):
    STATUS_CHOICES = [
        ('yes', 'Présent'),
        ('no', 'Absent'),
        ('maybe', 'Peut-être'),
    ]

    FINISH_CHOICES = [
        ('DNS', 'Non partant'),
        ('DNF', 'Non terminée'),
        ('finisher', 'Finisher'),
    ]

    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='presences')
    rider = models.ForeignKey('Rider', on_delete=models.CASCADE, related_name='race_presences')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    position = models.PositiveIntegerField(null=True, blank=True, help_text="Ex: 5 (pour 5ème)")
    finisher_status = models.CharField(max_length=20, choices=FINISH_CHOICES, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('race', 'rider')