from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Follow


def index(request):
    # Get all posts ordered by timestamp (newest first)
    posts = Post.objects.all()
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        'posts': page_obj,
        'user': request.user
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    """View to display user profile with their posts"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/error.html", {
            "message": "User not found."
        })
    
    # Get user's posts
    posts = Post.objects.filter(author=profile_user)
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if current user follows this profile user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    # Get follower and following counts
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    return render(request, "network/profile.html", {
        'profile_user': profile_user,
        'posts': page_obj,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'user': request.user
    })


@login_required
def following(request):
    """View to display posts from users that the current user follows"""
    # Get users that the current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get posts from those users
    posts = Post.objects.filter(author__in=following_users)
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        'posts': page_obj,
        'user': request.user
    })


@login_required
@require_POST
def create_post(request):
    """Handle creation of new posts"""
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Post content cannot be empty'}, status=400)
    
    if len(content) > 280:
        return JsonResponse({'error': 'Post content cannot exceed 280 characters'}, status=400)
    
    # Create new post
    post = Post.objects.create(
        content=content,
        author=request.user
    )
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'message': 'Post created successfully'
        })
    
    # Otherwise redirect to index
    return HttpResponseRedirect(reverse('index'))


@login_required
@require_POST
@csrf_exempt
def follow_toggle(request):
    """AJAX endpoint to toggle follow/unfollow status"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)
        
        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Prevent users from following themselves
        if target_user == request.user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
        
        # Check if already following
        follow_relationship = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).first()
        
        if follow_relationship:
            # Unfollow
            follow_relationship.delete()
            is_following = False
            action = 'unfollowed'
        else:
            # Follow
            Follow.objects.create(
                follower=request.user,
                following=target_user
            )
            is_following = True
            action = 'followed'
        
        # Get updated follower count
        followers_count = target_user.followers.count()
        
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'action': action,
            'followers_count': followers_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_exempt
def like_toggle(request):
    """AJAX endpoint to toggle like/unlike status for posts"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        
        if not post_id:
            return JsonResponse({'error': 'Post ID is required'}, status=400)
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        
        # Check if user has already liked the post
        if request.user in post.likes.all():
            # Unlike
            post.likes.remove(request.user)
            is_liked = False
            action = 'unliked'
        else:
            # Like
            post.likes.add(request.user)
            is_liked = True
            action = 'liked'
        
        # Get updated like count
        like_count = post.likes.count()
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'action': action,
            'like_count': like_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_exempt
def edit_post(request):
    """AJAX endpoint to edit posts"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        new_content = data.get('content', '').strip()
        
        if not post_id:
            return JsonResponse({'error': 'Post ID is required'}, status=400)
        
        if not new_content:
            return JsonResponse({'error': 'Post content cannot be empty'}, status=400)
        
        if len(new_content) > 280:
            return JsonResponse({'error': 'Post content cannot exceed 280 characters'}, status=400)
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        
        # Check if the user owns the post
        if post.author != request.user:
            return JsonResponse({'error': 'You can only edit your own posts'}, status=403)
        
        # Update the post content
        post.content = new_content
        post.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Post updated successfully',
            'new_content': new_content
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
