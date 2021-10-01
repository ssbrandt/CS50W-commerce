from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    active_listings = Listing.objects.filter(status=True)
    context = {'active_listings': active_listings}
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):

    form = ListingForm()

    if request.method == "POST":
        # will need to validate form and save.
        form = ListingForm(request.POST)
        creator = request.user
        if form.is_valid():
            form = form.save(commit=False)
            form.creator = creator
            form.save()
            return render(request, "auctions/index.html")
        else:
            #should add in error handling and return data back to form
            form = ListingForm()

    context = {'form': form}

    return render(request, "auctions/createlisting.html", context)

def view_listing(request, listing_id):

    listing = Listing.objects.get(id=listing_id)
    current_bid = Bid.objects.filter(listing=listing_id).latest().bid
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing=listing_id)
    context = {'listing':listing, 'current_bid':current_bid, 'bid_form':bid_form, 'comment_form':comment_form, 'comments':comments}

    return render(request, "auctions/listing.html", context)

def bid(request, listing_id):

    if request.method == 'POST':
        form = BidForm(request.POST)
        form = form.save(commit=False)
        form.bidder = request.user
        form.listing = Listing.objects.get(id=listing_id)
        starting_bid = Listing.objects.get(id=listing_id).starting_bid
        max_bid = Bid.objects.filter(listing=listing_id).latest().bid

        if form.bid >= starting_bid and form.bid > max_bid:
            form.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            form = BidForm(request.POST)
            listing = Listing.objects.get(id=listing_id)
            message = 'Bid must be greater than or equal to starting bid and higher then current bid.'
            context = {'form': form, 'listing':listing, 'message':message}
            return render(request, "auctions/listing.html", context)

def add_comment(request, listing_id):

    if request.method == 'POST':
        form = CommentForm(request.POST)
        form = form.save(commit=False)
        form.commenter = request.user
        form.listing = Listing.objects.get(id=listing_id)

        form.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def add_watchlist(request, listing_id):

    watchlist = Watchlist()
    watchlist.user = request.user
    watchlist.listing = Listing.objects.get(id=listing_id)
    watchlist.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def remove_watchlist(request, listing_id):
    watchlist = Watchlist.objects.filter(listing= Listing.objects.get(id=listing_id)).filter(user=request.user)
    watchlist.delete()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
