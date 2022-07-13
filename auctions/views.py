from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import ListingForm, BidForm, CommentForm

@login_required(login_url='login')
def index(request):
    active_listings = Listing.objects.filter(status=True)
    for current_listing in active_listings:
        if Bid.objects.filter(listing=current_listing):
            current_listing.current_bid = Bid.objects.filter(listing=current_listing.id).latest()
        else:
            current_listing.current_bid = None
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

@login_required(redirect_field_name='login')
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
            return HttpResponseRedirect(reverse("index"))

        else:
            #should add in error handling and return data back to form
            form = ListingForm()

    context = {'form': form}

    return render(request, "auctions/createlisting.html", context)

@login_required(login_url='login')
def view_listing(request, listing_id):

    listing = Listing.objects.get(id=listing_id)
    if Bid.objects.filter(listing=listing.id):
        current_bid = Bid.objects.filter(listing=listing_id).latest()
    else:
        current_bid = None
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing=listing_id)

    if Watchlist.objects.filter(user = request.user).filter(listing = listing):
        on_watchlist = True
    else:
        on_watchlist = False

    context = {'listing':listing, 'current_bid':current_bid, 'bid_form':bid_form, 'comment_form':comment_form, 'comments':comments, 'on_watchlist':on_watchlist}

    return render(request, "auctions/listing.html", context)

@login_required(login_url='login')
def bid(request, listing_id):

    if request.method == 'POST':
        form = BidForm(request.POST)
        form = form.save(commit=False)
        form.bidder = request.user
        form.listing = Listing.objects.get(id=listing_id)
        starting_bid = Listing.objects.get(id=listing_id).starting_bid

        if Bid.objects.filter(listing=form.listing.id):
            max_bid = Bid.objects.filter(listing=listing_id).latest().bid
        else:
            max_bid = 0
        # max_bid = Bid.objects.filter(listing=listing_id).latest().bid

        if form.bid >= starting_bid and form.bid > max_bid:
            form.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            form = BidForm()
            listing = Listing.objects.get(id=listing_id)
            # message = 'Bid must be greater than or equal to starting bid and higher then current bid.'
            # context = {'form': form, 'listing':listing, 'message':message}
            messages.error(request,'Bid must be greater than or equal to starting bid and higher then current bid.')
            context = {'form': form, 'listing':listing}
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            # return render(request, "auctions/listing.html", context)

@login_required(login_url='login')
def add_comment(request, listing_id):

    if request.method == 'POST':
        form = CommentForm(request.POST)
        form = form.save(commit=False)
        form.commenter = request.user
        form.listing = Listing.objects.get(id=listing_id)

        form.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def add_watchlist(request, listing_id):

    watchlist = Watchlist()
    watchlist.user = request.user
    watchlist.listing = Listing.objects.get(id=listing_id)
    watchlist.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def remove_watchlist(request, listing_id):
    watchlist = Watchlist.objects.filter(listing= Listing.objects.get(id=listing_id)).filter(user=request.user)
    watchlist.delete()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def view_watchlist(request):
    watchlist = Watchlist.objects.filter(user = request.user).values_list('listing', flat=True)
    watchlist_details = []

    for item in watchlist:
        watchlist_details.append(Listing.objects.get(id=item))

    context = {'watchlist':watchlist_details}

    return render(request, "auctions/watchlist.html", context)

@login_required(login_url='login')
def view_category(request):
    categories = set(Listing.objects.filter(category__isnull=False).values_list('category', flat=True))
    context = {'categories':categories}

    return render(request, 'auctions/category.html', context)

@login_required(login_url='login')
def view_category_items(request, category):
    listings = Listing.objects.filter(category=category)
    context = {'listings': listings, 'category':category}
    return render(request, 'auctions/category_items.html', context)

@login_required(login_url='login')
def close_auction(request, listing_id):
    #set status of listing to close (false)
    listing = Listing.objects.get(id=listing_id)
    listing.status = False
    listing.save()
    #set winner to true for bid
    if Bid.objects.filter(listing=listing_id):
        winning_bid = Bid.objects.filter(listing=listing_id).latest()
        winning_bid.winner = True
        winning_bid.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
