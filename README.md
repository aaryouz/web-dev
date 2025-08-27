# Finance Portfolio Tracker

A Flask-based web application for tracking stock portfolios, allowing users to buy and sell stocks with real-time pricing data.

## Features

- **User Authentication**: Secure user registration and login system
- **Stock Portfolio Management**: Track your stock holdings and cash balance
- **Real-time Stock Quotes**: Get current stock prices using live market data
- **Buy/Sell Stocks**: Execute stock transactions with validation
- **Transaction History**: View complete trading history
- **Portfolio Overview**: Dashboard showing current holdings and total portfolio value

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with CS50 SQL library
- **Session Management**: Flask-Session
- **Security**: Werkzeug password hashing
- **Stock Data**: CS50 Finance API for real-time quotes
- **Frontend**: HTML templates with Jinja2

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Finance/finance
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# The application will create finance.db automatically on first run
```

## Usage

1. Start the Flask development server:
```bash
flask run
```

2. Open your browser and navigate to `http://localhost:5000`

3. Register a new account or login with existing credentials

4. Use the application to:
   - View your portfolio on the homepage
   - Get stock quotes by symbol
   - Buy stocks (if you have sufficient cash)
   - Sell stocks from your holdings
   - View your transaction history

## Project Structure

```
finance/
├── app.py              # Main Flask application
├── helpers.py          # Utility functions
├── finance.db          # SQLite database
├── requirements.txt    # Python dependencies
├── static/            # CSS and static assets
│   ├── styles.css
│   ├── favicon.ico
│   └── I_heart_validator.png
└── templates/         # HTML templates
    ├── layout.html    # Base template
    ├── index.html     # Portfolio dashboard
    ├── login.html     # Login form
    ├── register.html  # Registration form
    ├── quote.html     # Stock quote lookup
    ├── quoted.html    # Quote results
    ├── buy.html       # Buy stocks form
    ├── sell.html      # Sell stocks form
    ├── history.html   # Transaction history
    └── apology.html   # Error messages
```

## Key Features

### Portfolio Dashboard
- Real-time portfolio valuation
- Current stock holdings with live prices
- Cash balance tracking
- Total portfolio value calculation

### Stock Trading
- Input validation for stock symbols and share quantities
- Real-time price lookup before transactions
- Sufficient funds/shares verification
- Transaction recording with timestamps

### Security
- Password hashing using Werkzeug
- Session-based authentication
- Login required decorators for protected routes
- SQL injection protection using parameterized queries

## Database Schema

The application uses SQLite with the following tables:
- `users`: User accounts with hashed passwords and cash balances
- `transactions`: All buy/sell transactions with timestamps

## Dependencies

- `cs50`: CS50's SQL library for database operations
- `Flask`: Web framework
- `Flask-Session`: Session management
- `pytz`: Timezone handling
- `requests`: HTTP requests for stock data

## License

This project is part of CS50's Introduction to Computer Science course.