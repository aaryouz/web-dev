from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max
from decimal import Decimal

from .models import User, Listing, Bid, Comment, Category, Watchlist
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    active_listings = Listing.objects.filter(active=True).order_by('-created_at')
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


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


@login_required
def create_listing(request):
    """Allow authenticated users to create new listings"""
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Create new listing
            listing = Listing.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                starting_bid=form.cleaned_data['starting_bid'],
                current_price=form.cleaned_data['starting_bid'],
                image_url=form.cleaned_data['image_url'],
                category=form.cleaned_data['category'],
                creator=request.user
            )
            messages.success(request, "Your listing has been created successfully!")
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm()
    
    return render(request, "auctions/create_listing.html", {
        "form": form,
        "categories": Category.objects.all()
    })


def listing_detail(request, listing_id):
    """Show individual listing with bid/comment/watchlist functionality"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Get forms for authenticated users
    bid_form = None
    comment_form = None
    is_watched = False
    
    if request.user.is_authenticated:
        bid_form = BidForm(listing=listing)
        comment_form = CommentForm()
        is_watched = listing.is_watched_by(request.user)
    
    # Get comments and bids
    comments = listing.comments.all()
    bids = listing.bids.all()
    highest_bid = listing.get_highest_bid()
    
    # Check if current user is the winner (if auction is closed)
    is_winner = False
    if not listing.active and highest_bid and request.user.is_authenticated:
        is_winner = highest_bid.user == request.user
    
    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "comments": comments,
        "bids": bids,
        "highest_bid": highest_bid,
        "is_watched": is_watched,
        "is_winner": is_winner,
        "bid_count": listing.get_bid_count()
    })


@login_required
def watchlist(request):
    """Show user's watchlist"""
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('listing')
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })


def categories(request):
    """Show all categories"""
    categories_list = Category.objects.all().order_by('name')
    
    # Add listing counts and recent listings for each category
    for category in categories_list:
        category.active_listings_count = Listing.objects.filter(category=category, active=True).count()
        category.total_listings_count = Listing.objects.filter(category=category).count()
        category.recent_listing = Listing.objects.filter(category=category, active=True).order_by('-created_at').first()
    
    return render(request, "auctions/categories.html", {
        "categories": categories_list
    })


def category_listings(request, category_id):
    """Show listings filtered by category"""
    category = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(category=category, active=True).order_by('-created_at')
    
    # Add watchlist status for authenticated users
    if request.user.is_authenticated:
        user_watchlist = set(Watchlist.objects.filter(user=request.user).values_list('listing_id', flat=True))
        for listing in listings:
            listing.is_watched = listing.id in user_watchlist
    
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })


@login_required
def add_to_watchlist(request, listing_id):
    """Add listing to user's watchlist"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Check if already in watchlist
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if created:
        messages.success(request, f"'{listing.title}' has been added to your watchlist.")
    else:
        messages.info(request, f"'{listing.title}' is already in your watchlist.")
    
    return redirect('listing_detail', listing_id=listing_id)


@login_required
def remove_from_watchlist(request, listing_id):
    """Remove listing from user's watchlist"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    try:
        watchlist_item = Watchlist.objects.get(user=request.user, listing=listing)
        watchlist_item.delete()
        messages.success(request, f"'{listing.title}' has been removed from your watchlist.")
    except Watchlist.DoesNotExist:
        messages.error(request, f"'{listing.title}' was not in your watchlist.")
    
    return redirect('listing_detail', listing_id=listing_id)


@login_required
def place_bid(request, listing_id):
    """Handle bid placement"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Check if listing is active
    if not listing.active:
        messages.error(request, "This auction is no longer active.")
        return redirect('listing_detail', listing_id=listing_id)
    
    # Check if user is trying to bid on their own listing
    if listing.creator == request.user:
        messages.error(request, "You cannot bid on your own listing.")
        return redirect('listing_detail', listing_id=listing_id)
    
    if request.method == "POST":
        form = BidForm(request.POST, listing=listing)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            
            # Create the bid
            bid = Bid.objects.create(
                user=request.user,
                listing=listing,
                amount=bid_amount
            )
            
            # Update listing's current price
            listing.current_price = bid_amount
            listing.save()
            
            messages.success(request, f"Your bid of ${bid_amount} has been placed successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    return redirect('listing_detail', listing_id=listing_id)


@login_required
def add_comment(request, listing_id):
    """Handle comment addition"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                user=request.user,
                listing=listing,
                content=form.cleaned_data['content']
            )
            messages.success(request, "Your comment has been added successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    return redirect('listing_detail', listing_id=listing_id)


@login_required
def close_auction(request, listing_id):
    """Allow listing creator to close auction"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Check if user is the creator of the listing
    if listing.creator != request.user:
        messages.error(request, "You can only close your own auctions.")
        return redirect('listing_detail', listing_id=listing_id)
    
    # Check if listing is already closed
    if not listing.active:
        messages.info(request, "This auction is already closed.")
        return redirect('listing_detail', listing_id=listing_id)
    
    # Close the listing
    listing.active = False
    listing.save()
    
    highest_bid = listing.get_highest_bid()
    if highest_bid:
        messages.success(request, f"Auction closed! The winner is {highest_bid.user.username} with a bid of ${highest_bid.amount}.")
    else:
        messages.success(request, "Auction closed with no bids.")
    
    return redirect('listing_detail', listing_id=listing_id)
