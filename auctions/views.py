from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Auction, Bid, Watchlist, Comment

from django.forms.models import model_to_dict


def index(request):
    auctions = Auction.objects.filter(status=True)

    return render(request, "auctions/index.html", {
        "auctions":auctions
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
def new(request):
    if request.method == 'POST':
        newAuction = Auction()

        newAuction.user = request.user
        newAuction.image = request.POST.get("image")
        newAuction.title = request.POST.get("title")
        newAuction.price = request.POST.get("price")
        newAuction.description = request.POST.get("description")

        if request.POST.get("category") != None:
            newAuction.category = request.POST.get("category")

        newAuction.save()

        return HttpResponseRedirect(reverse("index"))
        
    categories = [
        "Coins, Currency & Stamps",
        "Jewelry & Watches",
        "Fine & Decorative Arts",
        "Books", 
        "Design",
        "Cars, Motors & Automobilia",
        "Technology"
    ]

    return render(request, "auctions/new.html", {
        "categories": categories
        })


def listing(request, id):
    if request.method == "POST":

        auctionId = request.POST.get("auctionId")
        auction = Auction.objects.get(id=auctionId)

        # If user clicked the close button
        if request.POST.get("closeStatus") == "close":
            auction.status = False
            auction.save()
            
        # Default status
        watchlistStatus = False
        userHasHighest = False

        # If user placed a bid, save it
        if request.POST.get("bid") != None:
            bids = Bid.objects.filter(product=auction)
            
            for bid in bids:
                if int(request.POST.get("bid")) <= bid.value:
                    return render(request, "auctions/error.html", {
                "msg": "Ops! Your bid should be greater than the current one."
                })

            newBid = Bid()

            newBid.user = request.user
            newBid.product = auction
            newBid.value = request.POST.get("bid")
            newBid.save()

        # If user adds product to his watchlist
        if request.POST.get("status") == "add":
            addWatchList = Watchlist()

            addWatchList.user = request.user
            addWatchList.product = auction
            addWatchList.save()

            watchlistStatus = True

        # If user removes product from his watchlist
        elif request.POST.get("status") == "remove":
            rmvWatchList = Watchlist.objects.get(user=request.user, product=auction)
            rmvWatchList.delete()
            
            watchlistStatus = False

        # If user adds a comment
        if request.POST.get("userComment") != None:
            newComment = Comment()

            newComment.user = request.user
            newComment.product = auction
            newComment.comment = request.POST.get("userComment")
            newComment.save()

        return redirect('listing', id=auction.id)

    # Get auction
    try:
        auction = Auction.objects.get(id=id)
    except:
        return render(request, "auctions/error.html", {
            "msg": "Ops! We couldn't find the requested page."
            })
    
    # Get auction comments
    try:
        comments = Comment.objects.filter(product=auction)
    except:
        comments = False
    else:
        comments = Comment.objects.filter(product=auction)

    # Checks if product is in user's watchlist
    try:
        userWatchlist = Watchlist.objects.get(user=request.user, product=auction)
    except:
        watchlistStatus = False
    else:
        watchlistStatus = True

    # Get highest bid
    bids = Bid.objects.filter(product=auction)

    if bids.count() == 0:
        highestBid = False
    else:
        highestBid = auction.price
        for bid in bids:
            if highestBid == auction.price and bid.value >= highestBid:
                highestBid = bid.value
            elif bid.value > highestBid:
                highestBid = bid.value

    # Checks if user's bid is the highest one
    try:
        userBid = Bid.objects.get(product=auction, user=request.user).value
    except:
        userHasHighest = False
    else:
        if userBid == highestBid:
            userHasHighest = True
        else:
            userHasHighest = False

    # Checks if user is the creator of this auction
    if auction.user == request.user:
        userIsCreator = True
    else:
        userIsCreator = False

    # Checks if user is the current winner of this auction
    try:
        request.user == Bid.objects.get(product=auction, value=highestBid).user
    except:
        userIsWinner = False
    else:
        userIsWinner = True


    return render(request, "auctions/listing.html", {
        "auction": auction,
        "watchlisted": watchlistStatus,
        "highestBid": highestBid,
        "userHasHighest": userHasHighest,
        "userIsCreator": userIsCreator,
        "userIsWinner": userIsWinner,
        "comments": comments
    })


@login_required
def watchlist(request):
    userWatchlist = Watchlist.objects.filter(user=request.user)

    return render(request, "auctions/watchlist.html", {
        "userWatchlist": userWatchlist
        })


def categories(request):
    categories = [
        "Coins, Currency & Stamps",
        "Jewelry & Watches",
        "Fine & Decorative Arts",
        "Books", 
        "Design",
        "Cars, Motors & Automobilia",
        "Technology"
    ]

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listing(request, category):

    try:
        products = Auction.objects.filter(category=category)
    except:
        return render(request, "auctions/error.html", {
            "msg": "Sorry! We couldn't find an auction with this category."
            })

    return render(request, "auctions/category_listing.html", {
        "products": products
    })
        
    