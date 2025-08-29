from django.contrib import admin
from .models import User, Post, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    search_fields = ['username', 'email']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'timestamp', 'like_count']
    list_filter = ['timestamp']
    search_fields = ['content', 'author__username']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['follower__username', 'following__username']
