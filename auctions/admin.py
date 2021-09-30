from django.contrib import admin
from .models import Listing, Bid, User, Comment, Watchlist

# Register your models here.

admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Watchlist)
