from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # Listing URLs
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing_detail, name="listing_detail"),
    path("close/<int:listing_id>", views.close_auction, name="close_auction"),
    
    # Watchlist URLs
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/add/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/remove/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    
    # Bid and Comment URLs
    path("bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path("comment/<int:listing_id>", views.add_comment, name="add_comment"),
    
    # Category URLs
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category_listings, name="category_listings"),
]
