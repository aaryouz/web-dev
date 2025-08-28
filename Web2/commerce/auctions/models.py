from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='listings'
    )
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_listings'
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - ${self.current_price}"
    
    def get_highest_bid(self):
        """Return the highest bid for this listing"""
        return self.bids.order_by('-amount').first()
    
    def get_bid_count(self):
        """Return the number of bids on this listing"""
        return self.bids.count()
    
    def is_watched_by(self, user):
        """Check if listing is watched by a specific user"""
        if user.is_authenticated:
            return self.watchers.filter(user=user).exists()
        return False


class Bid(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bids'
    )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='bids'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['user', 'listing', 'amount']]
    
    def __str__(self):
        return f"{self.user.username} bid ${self.amount} on {self.listing.title}"


class Comment(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} commented on {self.listing.title}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='watchlist_items'
    )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='watchers'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'listing']]
    
    def __str__(self):
        return f"{self.user.username} watching {self.listing.title}"
