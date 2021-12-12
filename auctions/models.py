from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from datetime import date


class User(AbstractUser):
    pass

class Auction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="auctions")
    image = models.ImageField(upload_to="")
    title = models.CharField(max_length=64)
    price = models.FloatField()
    description = models.CharField(max_length=64)
    category = models.CharField(max_length=64, default="No category listed")
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="bids")
    value = models.FloatField()
    product = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.value} on {self.product} by {self.user}"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=64)
    product = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment on {self.product} by {self.user}"

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="watchlist")
    product = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name="usersWhoWatchlisted")

    def __str__(self):
        return f"{self.product} watchlisted by {self.user}"
    