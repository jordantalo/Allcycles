from django.db import models

# Create your models here.
class Article(models.Model):
    ARTICLE_CHOICES = {
        ('cuissard_court', 'Cuissard court'),
        ('cuissard_long', 'Cuissard long'),
        ('manchettes', 'Manchettes'),
        ('combi', 'Combinaison'),
        ('veste_hiver', 'Veste hiver'),
        ('veste_mi_saison', 'Veste mi saison'),
        ('gants', 'Gants'),
    }

    name = models.CharField("Nom de l'article", max_length=40, choices=ARTICLE_CHOICES)
    price = models.FloatField("Prix de l'article")

    def __str__(self):
        return f"[{self.name}](price: {self.price} euros)"

class Order(models.Model):
    first_name = models.CharField("Prenom de la personne associee a la commande", max_length=30)
    last_name = models.CharField("Nom de la personne associee a la commande", max_length=30)
    email = models.EmailField("Email de la personne associee a la commande")
    date = models.DateField("Date de la commande")
    club_price = models.FloatField("Prix total de la commande pour le club", default=0)
    rider_price = models.FloatField("Prix tota de la commande pour le coureur", default=0)

class OrderItem(models.Model):
    SIZE_CHOICES = {
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
    }

    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.PROTECT)
    size = models.CharField("Taille de l'article", max_length=3, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    is_club_paid = models.BooleanField(default=False)
