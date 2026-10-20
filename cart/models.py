from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie
# import the available regions for purchases
from .regions import REGION_CHOICES
# Create your models here.
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.user.username
    # store the geographic region where the order was placed
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        blank=True,
        default=""
    )

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order,
        on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name