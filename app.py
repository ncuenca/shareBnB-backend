import os

from flask import Flask, request, jsonify
from models import db, connect_db, User, Message, Listing, ListingPhoto
from sqlalchemy.exc import IntegrityError


database_url = os.environ.get('DATABASE_URL', 'postgresql:///sharebnb')

# fix incorrect database URIs currently returned by Heroku's pg setup
database_url = database_url.replace('postgres://', 'postgresql://')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)


##############################################################################
# Listing Routes

@app.route('/listings')
def get_listings():
    """If search term included, gets filtered listings. Otherwise,
        gets all listings.
    """

    search = request.args.get('q')

    if not search: 
        listings = Listing.query.all()
    else: 
        listings = Listing.query.filter(Listing.title.like(f"%{search}%")).all()

    serialized = [listing.serialize() for listing in listings]
    return (jsonify(listings=serialized))


@app.route('/listings', methods=["POST"])
def add_listing():
    """Handle add listing.

    Create new listing and add to DB.
    """

    title = request.json["title"]
    price = request.json["price"]
    address = request.json["address"]
    details = request.json["details"]
    host = request.json["host"]

    new_listing = Listing(
        title=title,
        price=price,
        address=address,
        details=details,
        host=host,
    )

    db.session.add(new_listing)
    db.session.commit()

    serialized = new_listing.serialize()

    return (jsonify(listing=serialized), 201)


@app.route('/listings/<int:id>')
def get_listing(id): 
    """Gets listing by id."""

    listing = Listing.query.get_or_404(id)

    serialized = listing.serialize()

    return(jsonify(serialized))


##############################################################################
# User Routes

@app.route('/users', methods=["POST"])
def sign_up(): 
    """Handles user sign up."""

    username = request.json["username"]
    password = request.json["password"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    email = request.json["email"]
    phone = request.json["phone"]

    try: 
        user = User.signup(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
    except IntegrityError as error:
        return(jsonify(error=error))
    
    return (jsonify(user=user.serialize()))


