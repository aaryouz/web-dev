from django.contrib import admin
from .models import Listing, Bid, Comment, Category

# Register your models here.


class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'current_price', 'active', 'created_at')
    list_filter = ('active', 'category', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        """Return a truncated version of the comment content for list display"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Content Preview'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Register models with their admin classes
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
