from django import forms
from .models import Listing, Bid


class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        exclude = ['status', 'creator']

class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        exclude = ['bidder', 'listing', 'winning_bid']
