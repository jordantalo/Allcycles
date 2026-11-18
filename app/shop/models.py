from django.db import models

# Create your models here.

class PackageGroup(models.Model):
    name = models.CharField(max_length=10, verbose_name="Nom du groupe")
    access_code = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la campagne")
    start_date = models.DateField(verbose_name="Date d'ouverture")
    end_date = models.DateField(verbose_name="Date de fermeture")
    is_active = models.BooleanField(default=False, verbose_name="Campagne active")

    def save(self, *args, **kwargs):

        if self.is_active:
             Campaign.objects.all().filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.name}] - [start: {self.start_date}] - [end: {self.end_date}]"

class Article(models.Model):
    ARTICLE_CHOICES = {
        ('cuissard_court', 'Cuissard court'),
        ('cuissard_long', 'Cuissard long'),
        ('manchettes', 'Manchettes'),
        ('combi', 'Combinaison'),
        ('veste_hiver', 'Veste hiver'),
        ('veste_mi_saison', 'Veste mi saison'),
        ('gants', 'Gants'),
        ('coupe_vent', 'Coupe vent'),
        ('maillot_court', 'Maillot'),
    }

    name = models.CharField("Nom de l'article", max_length=40, choices=ARTICLE_CHOICES)
    price = models.FloatField("Prix de l'article")

    package_config = models.JSONField(default=dict, blank=True, help_text='Ex: {"DN3": 2, "ACCESS": 1}')

    def __str__(self):
        return f"[{self.name}](price: {self.price} euros)"

class GroupeArticleConfig(models.Model):
    group = models.ForeignKey(PackageGroup, on_delete=models.CASCADE, related_name="package_items")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="group_dotations")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('group', 'article')

    def __str__(self):
        return f"{self.group.name} - {self.article.name} ({self.quantity})"

class Order(models.Model):
    first_name = models.CharField("Prenom de la personne associee a la commande", max_length=30)
    last_name = models.CharField("Nom de la personne associee a la commande", max_length=30)
    email = models.EmailField("Email de la personne associee a la commande")
    date = models.DateField("Date de la commande")
    club_cost = models.FloatField("Cout pour le club", default=0)
    rider_cost = models.FloatField("Cout pour le coureur", default=0)
    total_cost = models.FloatField("Prix total de la commande", default=0)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="orders", verbose_name="Campagne")

    def __str__(self):
        return f"{self.id} - ({self.date}) - [{self.last_name} {self.first_name}] - [{self.email}]"

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
    order = models.ForeignKey('Order', on_delete=models.PROTECT, related_name='items')
    size = models.CharField("Taille de l'article", max_length=3, choices=SIZE_CHOICES, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)

    article_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"[{self.article.name} - {self.size} - {self.quantity}][order_id: {self.order.id}]"

