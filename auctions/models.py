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
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # need to add relationship to User

    def __str__(self):
        return f'Listing {self.id}: {self.title}'
#
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=20, decimal_places=2)
    winner = models.BooleanField(default=False)

    def __str__(self):
        return f'Bid by {self.bidder} for {self.listing} at {self.bid}'

    #supports finding the max bid by using the latest field which returns the max bid
    class Meta:
        get_latest_by = 'bid'


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=mdoels.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f'Comment #{self.id} on {self.listing} by {self.commenter}'
