from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2)
    listing_image = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    status = models.BooleanField(default=True)
    # need to add relationship to User

    def __str__(self):
        return f'Listing {self.id}: {self.title}'
#
# class Bid(models.Model):
#     pass
#
# class Comment(models.Model):
#     pass
