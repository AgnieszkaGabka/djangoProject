from django.db import models

from django.db import models
from django.db.models import CASCADE


CHANGE = (
    (1, "przegląd techniczny"),
    (2, "filtr oleju"),
    (3, "filtr powietrza"),
    (4, "klocki hamulcowe"),
    (5, "filtr paliwa"),
    (6, "tarcze hamulcowe"),
    (7, "filtr kabinowy"),
    (8, "akumulator"),
    (9, "rozrząd"),
    (10, "zmiana na opony letnie"),
    (11, "zmiana na opony zimowe"),
)


FUEL = (
    (1, "Benzyna 95"),
    (2, "Benzyna 98"),
    (3, "Benzyna 100"),
    (4, "Diesel B7"),
    (5, "Diesel B10"),
    (6, "Diesel XTL"),
    (7, "Gaz"),
)

REPLENISHMENT = (
    (1, "uzupełnienie oleju silnikowego"),
    (2, "uzupełnienie płynu hamulcowego"),
    (3, "uzupełnienie płynu do spryskiwaczy"),
)


class Car(models.Model):
    production_date = models.DateField()
    brand = models.CharField(max_length=124)
    color = models.CharField(max_length=124)


class User(models.Model):
    name = models.CharField(max_length=124)
    purchase_date = models.DateField()
    sale_date = models.DateField(null=True)
    car = models.ManyToManyField(Car)


class Usercar(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    car = models.ForeignKey(Car, on_delete=CASCADE)


class Change(models.Model):
    change_type = models.IntegerField(choices=CHANGE)
    change_date = models.DateField()
    car = models.ForeignKey(Car, on_delete=CASCADE)


class Refueling(models.Model):
    fuel_type = models.IntegerField(choices=FUEL)
    amount_fueled = models.FloatField()
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2)
    kilometers_traveled = models.IntegerField()
    car = models.ForeignKey(Car, on_delete=CASCADE)


class Replenishment(models.Model):
    fluid_type = models.IntegerField(choices=REPLENISHMENT)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    car = models.ForeignKey(Car, on_delete=CASCADE)
