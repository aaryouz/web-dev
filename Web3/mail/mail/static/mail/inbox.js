document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Add event listener to compose form
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function send_email(event) {
  // Prevent default form submission
  event.preventDefault();

  // Get form data
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send email via POST to /emails API
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    // Handle the response
    if (result.error) {
      alert('Error: ' + result.error);
    } else {
      // Email sent successfully, load sent mailbox
      alert('Email sent successfully!');
      load_mailbox('sent');
    }
  })
  .catch(error => {
    console.error('Error sending email:', error);
    alert('Error sending email. Please try again.');
  });
}

function load_mailbox(mailbox) {
  // Set current mailbox
  currentMailbox = mailbox;
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  // Hide email view if it exists
  const emailView = document.querySelector('#email-view');
  if (emailView) {
    emailView.style.display = 'none';
  }

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch emails for this mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Render emails in the mailbox
    render_emails(emails, mailbox);
  })
  .catch(error => {
    console.error('Error loading mailbox:', error);
    document.querySelector('#emails-view').innerHTML += '<p>Error loading emails. Please try again.</p>';
  });
}

function render_emails(emails, mailbox) {
  const emailsView = document.querySelector('#emails-view');
  
  // If no emails, show message
  if (emails.length === 0) {
    emailsView.innerHTML += '<p>No emails in this mailbox.</p>';
    return;
  }

  // Create container for emails
  const emailsContainer = document.createElement('div');
  
  // Render each email
  emails.forEach(email => {
    const emailDiv = document.createElement('div');
    emailDiv.className = `email-item p-3 mb-2 ${email.read ? 'read' : 'unread'}`;
    emailDiv.style.cursor = 'pointer';
    
    // Format timestamp
    const timestamp = new Date(email.timestamp).toLocaleString();
    
    // Create email content
    let senderOrRecipient;
    if (mailbox === 'sent') {
      // For sent emails, show recipients
      senderOrRecipient = `To: ${email.recipients.join(', ')}`;
    } else {
      // For inbox/archive, show sender
      senderOrRecipient = `From: ${email.sender}`;
    }
    
    emailDiv.innerHTML = `
      <div class="row">
        <div class="col-md-3">
          <strong>${senderOrRecipient}</strong>
        </div>
        <div class="col-md-6">
          <span>${email.subject || '(No Subject)'}</span>
        </div>
        <div class="col-md-3 text-right">
          <small class="text-muted">${timestamp}</small>
        </div>
      </div>
    `;
    
    // Add click event to view email details
    emailDiv.addEventListener('click', () => view_email(email.id));
    
    emailsContainer.appendChild(emailDiv);
  });
  
  emailsView.appendChild(emailsContainer);
}

function view_email(email_id) {
  // Fetch individual email details
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Hide other views and show email details
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    
    // Create or update email view
    let emailView = document.querySelector('#email-view');
    if (!emailView) {
      emailView = document.createElement('div');
      emailView.id = 'email-view';
      document.body.appendChild(emailView);
    }
    
    emailView.style.display = 'block';
    
    // Format timestamp
    const timestamp = new Date(email.timestamp).toLocaleString();
    
    // Determine current mailbox for archive button visibility
    const currentMailbox = getCurrentMailbox();
    
    // Create action buttons HTML
    let actionButtons = '';
    
    // Archive/Unarchive button (only show for inbox and archive emails)
    if (currentMailbox === 'inbox' || currentMailbox === 'archive') {
      if (email.archived) {
        actionButtons += `<button class="btn btn-warning mr-2" onclick="unarchive_email(${email.id})">Unarchive</button>`;
      } else {
        actionButtons += `<button class="btn btn-primary mr-2" onclick="archive_email(${email.id})">Archive</button>`;
      }
    }
    
    // Reply button (show for all emails except sent)
    if (currentMailbox !== 'sent') {
      actionButtons += `<button class="btn btn-success" onclick="reply_email(${email.id})">Reply</button>`;
    }
    
    // Display email details
    emailView.innerHTML = `
      <div class="container mt-3">
        <button class="btn btn-secondary mb-3" onclick="go_back()">← Back</button>
        <div class="card">
          <div class="card-header">
            <h4>${email.subject || '(No Subject)'}</h4>
            <div class="email-meta">
              <p><strong>From:</strong> ${email.sender}</p>
              <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
              <p><strong>Date:</strong> ${timestamp}</p>
            </div>
            <div class="email-actions mt-3">
              ${actionButtons}
            </div>
          </div>
          <div class="card-body">
            <div class="email-body" style="white-space: pre-wrap;">${email.body}</div>
          </div>
        </div>
      </div>
    `;
    
    // Mark email as read if it wasn't already
    if (!email.read) {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      });
    }
  })
  .catch(error => {
    console.error('Error loading email:', error);
    alert('Error loading email. Please try again.');
  });
}

// Global variable to track current mailbox
let currentMailbox = 'inbox';

function getCurrentMailbox() {
  return currentMailbox;
}

function archive_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: true
    })
  })
  .then(() => {
    // Return to inbox after archiving
    load_mailbox('inbox');
  })
  .catch(error => {
    console.error('Error archiving email:', error);
    alert('Error archiving email. Please try again.');
  });
}

function unarchive_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: false
    })
  })
  .then(() => {
    // Return to inbox after unarchiving
    load_mailbox('inbox');
  })
  .catch(error => {
    console.error('Error unarchiving email:', error);
    alert('Error unarchiving email. Please try again.');
  });
}

function reply_email(email_id) {
  // Fetch email details to pre-populate compose form
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Pre-populate compose fields
    document.querySelector('#compose-recipients').value = email.sender;
    
    // Handle subject with "Re:" prefix, avoid duplicating "Re:"
    let subject = email.subject || '';
    if (!subject.toLowerCase().startsWith('re:')) {
      subject = 'Re: ' + subject;
    }
    document.querySelector('#compose-subject').value = subject;
    
    // Format timestamp for reply body
    const timestamp = new Date(email.timestamp).toLocaleString();
    const replyBody = `\n\nOn ${timestamp} ${email.sender} wrote:\n${email.body.split('\n').map(line => '> ' + line).join('\n')}`;
    document.querySelector('#compose-body').value = replyBody;
    
    // Focus on the body textarea for immediate typing
    document.querySelector('#compose-body').focus();
    // Move cursor to the beginning
    document.querySelector('#compose-body').setSelectionRange(0, 0);
  })
  .catch(error => {
    console.error('Error loading email for reply:', error);
    alert('Error loading email for reply. Please try again.');
  });
}

function go_back() {
  // Hide email view and show emails view
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
}