
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # Profile and following functionality
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    
    # Post functionality
    path("create_post", views.create_post, name="create_post"),
    
    # AJAX endpoints
    path("follow_toggle", views.follow_toggle, name="follow_toggle"),
    path("like_toggle", views.like_toggle, name="like_toggle"),
    path("edit_post", views.edit_post, name="edit_post")
]
