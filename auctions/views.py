from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid
from .forms import ListingForm, BidForm


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
    form = BidForm()
    context = {'listing':listing, 'form':form}

    return render(request, "auctions/listing.html", context)

def bid(request, listing_id):
    #if request is post, then take bid and see if it's greater or equal to starting bid and max current bid
    # if so save bid
    # if not return error message

    if request.method == 'POST':
        form = BidForm(request.POST)
        form = form.save(commit=False)
        form.bidder = request.user
        form.listing = Listing.objects.get(id=listing_id)
        starting_bid = Listing.objects.get(id=listing_id).starting_bid
        if form.bid >= starting_bid:
            form.save()
            return redirect('index')
        else:
            print("caught error")
