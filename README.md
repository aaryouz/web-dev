# Web Development Projects Collection

A comprehensive collection of 6 web development projects showcasing progression from basic HTML to advanced Django and Flask applications, built as part of CS50's Web Programming with Python and JavaScript course.

## Projects Overview

### 🔍 [Web0 - Search](./Web0/)
**HTML/CSS Frontend** - Google Search Clone
- Clean, responsive search interface mimicking Google's design
- Advanced search functionality with filters
- Image search with grid layout
- Pure HTML/CSS implementation focusing on UI/UX fundamentals

### 📚 [Web1 - Wiki](./Web1/)
**Django Application** - Encyclopedia Platform
- Full-featured wiki encyclopedia with Markdown support
- Create, edit, and search encyclopedia entries
- Random page functionality
- Django templates and URL routing
- File-based entry storage system

### 🛒 [Web2 - Commerce](./Web2/)
**Django E-commerce** - Auction Site
- Complete auction platform with user authentication
- Create listings, place bids, and manage watchlists
- Category-based browsing and search functionality
- Django models, forms, and admin integration
- User dashboard with active listings and bid history

### 📧 [Web3 - Mail](./Web3/)
**Single Page Application** - Email Client
- Gmail-like interface built with JavaScript and Django REST API
- Send, receive, and organize emails
- Mark emails as read/unread and archive functionality
- Dynamic content loading without page refresh
- Modern SPA architecture with Django backend

### 🌐 [Web4 - Network](./project4/)
**Django Social Network** - Twitter-like Social Platform
- User registration and authentication system
- Create, edit, and like posts
- Follow/unfollow users functionality
- Personalized timeline and user profiles
- Pagination and responsive design
- Django REST API for dynamic interactions

### 💰 [Finance - Portfolio Tracker](./finance/)
**Flask Application** - Stock Trading Platform
- Real-time stock portfolio management
- Buy/sell stocks with live pricing data
- User authentication and session management
- Transaction history and portfolio analytics
- Integration with financial APIs

## Technologies Used

| Project | Frontend | Backend | Database | Key Features |
|---------|----------|---------|----------|--------------|
| Web0 | HTML, CSS | None | None | Responsive design, CSS Grid/Flexbox |
| Web1 | HTML, Django Templates | Django | File system | Markdown rendering, CRUD operations |
| Web2 | HTML, Django Templates | Django | SQLite | User auth, Forms, Admin panel |
| Web3 | JavaScript, HTML | Django REST | SQLite | AJAX, SPA architecture, API design |
| Web4 | JavaScript, HTML, Django Templates | Django | SQLite | Social features, Follow system, REST API |
| Finance | HTML, Jinja2 | Flask | SQLite | Session management, Real-time data |

## Getting Started

Each project is contained in its own directory with specific setup instructions. Generally:

1. **Clone the repository:**
```bash
git clone https://github.com/aaryouz/web-dev.git
cd web-dev
```

2. **Navigate to desired project:**
```bash
cd Web1/wiki  # Example for Django wiki project
cd project4   # Example for Django social network project
```

3. **Install dependencies and run:**
```bash
# For Django projects
pip install django
python manage.py migrate
python manage.py runserver

# For Flask projects
pip install flask cs50
flask run
```

## Learning Progression

This collection demonstrates progressive learning in web development:

1. **Web0**: Foundation in HTML/CSS and responsive design
2. **Web1**: Introduction to Django framework and server-side rendering
3. **Web2**: Advanced Django with user authentication and database relations
4. **Web3**: Modern SPA development with JavaScript and REST APIs
5. **Web4**: Full-featured social network with advanced Django patterns and user interactions
6. **Finance**: Flask framework with session management and external API integration

## Project Highlights

- **Responsive Design**: All projects implement mobile-first, responsive layouts
- **Security**: Proper authentication, CSRF protection, and input validation
- **Database Design**: Efficient schema design with proper relationships
- **API Integration**: Real-time data fetching from external services
- **Modern Architecture**: Progression from server-side rendering to SPA patterns

## Course Context

These projects were developed as part of **CS50's Web Programming with Python and JavaScript**, demonstrating practical application of:
- Frontend technologies (HTML, CSS, JavaScript)
- Backend frameworks (Django, Flask)
- Database design and management
- User authentication and security
- API design and consumption
- Modern web development patterns

## License

This project collection is part of CS50's Web Programming with Python and JavaScript course.