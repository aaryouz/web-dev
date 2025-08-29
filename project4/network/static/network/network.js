// Network JavaScript functionality for AJAX interactions
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from meta tag or form
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name=csrf-token]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        const formToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (formToken) {
            return formToken.value;
        }
        return '';
    }

    // Generic function to show messages to user
    function showMessage(message, type = 'info') {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        
        // Insert at top of body
        const container = document.querySelector('.body') || document.body;
        container.insertBefore(messageDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // Follow/Unfollow functionality
    function setupFollowButtons() {
        document.querySelectorAll('.follow-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const username = this.dataset.username;
                const isFollowing = this.dataset.following === 'true';
                
                // Disable button during request
                this.disabled = true;
                const originalText = this.textContent;
                this.textContent = isFollowing ? 'Unfollowing...' : 'Following...';
                
                fetch('/follow_toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        username: username
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showMessage(data.error, 'danger');
                        this.textContent = originalText;
                    } else {
                        // Update button
                        this.dataset.following = data.is_following;
                        this.textContent = data.is_following ? 'Unfollow' : 'Follow';
                        this.className = data.is_following ? 
                            'btn btn-outline-danger follow-btn' : 
                            'btn btn-primary follow-btn';
                        
                        // Update follower count
                        const followersCount = document.getElementById('followers-count');
                        if (followersCount) {
                            followersCount.textContent = data.followers_count;
                        }
                        
                        // Update following count
                        const followingCount = document.getElementById('following-count');
                        if (followingCount) {
                            followingCount.textContent = data.following_count;
                        }
                        
                        showMessage(
                            `You are now ${data.is_following ? 'following' : 'not following'} ${username}`,
                            'success'
                        );
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An error occurred. Please try again.', 'danger');
                    this.textContent = originalText;
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    // Like/Unlike functionality
    function setupLikeButtons() {
        document.querySelectorAll('.like-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const postId = this.dataset.postId;
                const isLiked = this.dataset.liked === 'true';
                
                // Disable button during request
                this.disabled = true;
                
                fetch('/like_toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        post_id: postId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showMessage(data.error, 'danger');
                    } else {
                        // Update button
                        this.dataset.liked = data.is_liked;
                        const heartIcon = this.querySelector('i');
                        if (heartIcon) {
                            heartIcon.className = data.is_liked ? 
                                'fas fa-heart text-danger' : 
                                'far fa-heart';
                        }
                        
                        // Update like count
                        const likeCount = document.getElementById(`like-count-${postId}`);
                        if (likeCount) {
                            likeCount.textContent = data.like_count;
                        }
                        
                        // Update button text
                        const buttonText = this.querySelector('.like-text');
                        if (buttonText) {
                            buttonText.textContent = data.is_liked ? 'Unlike' : 'Like';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An error occurred. Please try again.', 'danger');
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    // Edit post functionality
    function setupEditButtons() {
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const postId = this.dataset.postId;
                const postContent = document.getElementById(`post-content-${postId}`);
                const originalContent = postContent.textContent.trim();
                
                // Create textarea for editing
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control';
                textarea.value = originalContent;
                textarea.rows = 3;
                
                // Create save and cancel buttons
                const buttonGroup = document.createElement('div');
                buttonGroup.className = 'mt-2';
                
                const saveBtn = document.createElement('button');
                saveBtn.className = 'btn btn-success btn-sm mr-2';
                saveBtn.textContent = 'Save';
                
                const cancelBtn = document.createElement('button');
                cancelBtn.className = 'btn btn-secondary btn-sm';
                cancelBtn.textContent = 'Cancel';
                
                buttonGroup.appendChild(saveBtn);
                buttonGroup.appendChild(cancelBtn);
                
                // Replace content with textarea
                postContent.style.display = 'none';
                this.style.display = 'none';
                postContent.parentNode.insertBefore(textarea, postContent.nextSibling);
                postContent.parentNode.insertBefore(buttonGroup, textarea.nextSibling);
                
                // Focus on textarea
                textarea.focus();
                
                // Cancel editing
                cancelBtn.addEventListener('click', function() {
                    textarea.remove();
                    buttonGroup.remove();
                    postContent.style.display = 'block';
                    button.style.display = 'inline-block';
                });
                
                // Save changes
                saveBtn.addEventListener('click', function() {
                    const newContent = textarea.value.trim();
                    
                    if (!newContent) {
                        showMessage('Post content cannot be empty.', 'warning');
                        return;
                    }
                    
                    if (newContent === originalContent) {
                        // No changes made
                        cancelBtn.click();
                        return;
                    }
                    
                    // Disable save button
                    saveBtn.disabled = true;
                    saveBtn.textContent = 'Saving...';
                    
                    fetch('/edit_post', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            post_id: postId,
                            content: newContent
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            showMessage(data.error, 'danger');
                            saveBtn.disabled = false;
                            saveBtn.textContent = 'Save';
                        } else {
                            // Update post content
                            postContent.textContent = data.content;
                            
                            // Clean up editing interface
                            textarea.remove();
                            buttonGroup.remove();
                            postContent.style.display = 'block';
                            button.style.display = 'inline-block';
                            
                            showMessage('Post updated successfully!', 'success');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showMessage('An error occurred. Please try again.', 'danger');
                        saveBtn.disabled = false;
                        saveBtn.textContent = 'Save';
                    });
                });
                
                // Handle Enter key (save) and Escape key (cancel)
                textarea.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && e.ctrlKey) {
                        e.preventDefault();
                        saveBtn.click();
                    } else if (e.key === 'Escape') {
                        e.preventDefault();
                        cancelBtn.click();
                    }
                });
            });
        });
    }

    // Initialize all functionality
    setupFollowButtons();
    setupLikeButtons();
    setupEditButtons();
    
    // Re-initialize when new content is loaded (for pagination, etc.)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if any added nodes contain our buttons
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.querySelector && 
                            (node.querySelector('.follow-btn') || 
                             node.querySelector('.like-btn') || 
                             node.querySelector('.edit-btn'))) {
                            setupFollowButtons();
                            setupLikeButtons();
                            setupEditButtons();
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});