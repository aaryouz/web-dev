from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """
    Display an individual encyclopedia entry.
    """
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"Entry '{title}' not found."
        })
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(content)
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })


def edit(request, title):
    """
    Edit an encyclopedia entry.
    """
    if request.method == "POST":
        # Save the edited content
        content = request.POST.get("content", "")
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    # GET request - show form with current content
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"Entry '{title}' not found."
        })
    
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


def search(request):
    """
    Handle search functionality for encyclopedia entries.
    """
    # Handle both GET and POST requests for backward compatibility
    query = ""
    if request.method == "POST":
        query = request.POST.get("q", "").strip()
    else:
        query = request.GET.get("q", "").strip()
    
    if not query:
        return redirect("index")
    
    # Get all entries
    entries = util.list_entries()
    
    # Check for exact match (case-insensitive)
    for entry in entries:
        if entry.lower() == query.lower():
            return redirect("entry", title=entry)
    
    # Find partial matches (case-insensitive)
    matches = []
    for entry in entries:
        if query.lower() in entry.lower():
            matches.append(entry)
    
    return render(request, "encyclopedia/search_results.html", {
        "query": query,
        "matches": matches
    })


def new_page(request):
    """
    Create a new encyclopedia entry.
    """
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")
        
        if not title:
            return render(request, "encyclopedia/new.html", {
                "error": "Title is required.",
                "title": title,
                "content": content
            })
        
        # Check if entry already exists (case-insensitive)
        existing_entries = util.list_entries()
        if any(entry.lower() == title.lower() for entry in existing_entries):
            return render(request, "encyclopedia/new.html", {
                "error": f"An entry with the title '{title}' already exists.",
                "title": title,
                "content": content
            })
        
        # Save the new entry and redirect to it
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    # GET request - show form for creating new entry
    return render(request, "encyclopedia/new.html")


def random_page(request):
    """
    Redirect to a random encyclopedia entry.
    """
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return redirect("entry", title=random_entry)
    else:
        return redirect("index")


