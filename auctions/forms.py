from django import forms
from .models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        exclude = ['status', 'creator']

class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        exclude = ['bidder', 'listing', 'winner']

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ['commenter', 'listing']
