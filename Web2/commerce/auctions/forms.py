from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Category


class ListingForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter listing title'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter detailed description'
        })
    )
    starting_bid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        })
    )
    image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter image URL (optional)'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select a category (optional)",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data['starting_bid']
        if starting_bid <= 0:
            raise ValidationError("Starting bid must be greater than 0.")
        return starting_bid


class BidForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Enter your bid'
        })
    )

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError("Bid amount must be greater than 0.")
        
        if self.listing:
            current_price = self.listing.current_price
            if amount <= current_price:
                raise ValidationError(f"Bid must be higher than current price of ${current_price}.")
        
        return amount


class CommentForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add your comment...'
        }),
        max_length=1000
    )

    def clean_content(self):
        content = self.cleaned_data['content']
        if not content.strip():
            raise ValidationError("Comment cannot be empty.")
        return content.strip()