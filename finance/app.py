import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get user's current cash balance
    rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = rows[0]["cash"]
    
    # Get user's stock holdings
    holdings = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions 
        WHERE user_id = ? 
        GROUP BY symbol 
        HAVING SUM(shares) > 0
    """, session["user_id"])
    
    # Calculate current values for each holding
    total_value = cash
    for holding in holdings:
        stock = lookup(holding["symbol"])
        if stock:
            holding["name"] = stock["name"]
            holding["price"] = stock["price"]
            holding["total"] = holding["total_shares"] * stock["price"]
            total_value += holding["total"]
        else:
            holding["name"] = "Unknown"
            holding["price"] = 0
            holding["total"] = 0
    
    return render_template("index.html", holdings=holdings, cash=cash, total_value=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Validate symbol input
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        
        # Validate shares input
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except (ValueError, TypeError):
            return apology("shares must be a positive integer", 400)
        
        # Look up the stock symbol
        stock = lookup(symbol.upper())
        if stock is None:
            return apology("invalid symbol", 400)
        
        # Calculate total cost
        total_cost = shares * stock["price"]
        
        # Get user's current cash
        rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if len(rows) != 1:
            return apology("user not found", 400)
        
        user_cash = rows[0]["cash"]
        
        # Check if user has enough cash
        if user_cash < total_cost:
            return apology("can't afford", 400)
        
        # Update user's cash
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])
        
        # Record the transaction
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], stock["symbol"], shares, stock["price"]
        )
        
        # Flash success message
        flash(f"Bought {shares} shares of {stock['symbol']} for {usd(total_cost)}!")
        
        # Redirect to homepage
        return redirect("/")
    
    else:
        # User reached route via GET (display buy form)
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get all transactions for the current user
    transactions = db.execute("""
        SELECT symbol, shares, price, timestamp 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, session["user_id"])
    
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Validate that symbol was provided
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        
        # Use lookup helper function to get stock data
        stock = lookup(symbol)
        
        # If stock not found, return apology
        if stock is None:
            return apology("symbol not found", 400)
        
        # If stock found, render results template with stock info
        return render_template("quoted.html", stock=stock)
    
    # Handle GET requests by rendering quote lookup form
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        
        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)
        
        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        
        # Query database for username to check if it already exists
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        
        # Ensure username doesn't already exist
        if len(rows) != 0:
            return apology("username already exists", 400)
        
        # Insert new user into database
        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password"))
        )
        
        # Remember which user has logged in
        session["user_id"] = user_id
        
        # Redirect user to home page
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Validate symbol input
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        
        # Validate shares input
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except (ValueError, TypeError):
            return apology("shares must be a positive integer", 400)
        
        # Get user's current holdings for this symbol
        holdings = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ?",
            session["user_id"], symbol.upper()
        )
        
        if not holdings or holdings[0]["total_shares"] is None or holdings[0]["total_shares"] < shares:
            return apology("not enough shares", 400)
        
        # Look up the current stock price
        stock = lookup(symbol.upper())
        if stock is None:
            return apology("invalid symbol", 400)
        
        # Calculate total sale amount
        total_sale = shares * stock["price"]
        
        # Record the sale transaction (negative shares to indicate sale)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], stock["symbol"], -shares, stock["price"]
        )
        
        # Update user's cash (add sale proceeds)
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_sale, session["user_id"])
        
        # Flash success message
        flash(f"Sold {shares} shares of {stock['symbol']} for {usd(total_sale)}!")
        
        # Redirect to homepage
        return redirect("/")
    
    else:
        # User reached route via GET (display sell form)
        # Get user's current stock holdings
        holdings = db.execute("""
            SELECT symbol, SUM(shares) as total_shares 
            FROM transactions 
            WHERE user_id = ? 
            GROUP BY symbol 
            HAVING SUM(shares) > 0
        """, session["user_id"])
        
        return render_template("sell.html", holdings=holdings)
