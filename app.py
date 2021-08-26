import os

from flask import Flask, request, jsonify
from models import Message, db, connect_db, User, Listing, ListingPhoto
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
# from werkzeug.security import secure_filename
from helpers import upload_file_to_s3
from my_secrets import S3_BUCKET
import jwt


database_url = os.environ.get('DATABASE_URL', 'postgresql:///sharebnb')

# fix incorrect database URIs currently returned by Heroku's pg setup
database_url = database_url.replace('postgres://', 'postgresql://')

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "super secret secret key")

connect_db(app)


##############################################################################
# Auth Routes / Functions

@app.route('/login', methods=['POST'])
def login():
    # breakpoint()
    username = request.json['username']
    password = request.json['password']
    
    user = User.authenticate(username, password)
    if user:
        token = createJWT(user)
        return (jsonify(user=user.serialize(),token=token))
    return jsonify(error='Invalid login'), 401

def createJWT(user):
    """ Creates JWT token with username and admin in payload. """
    payload = { 'username':user.username, 'is_admin':user.is_admin }
    token = jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
    return token

def authenticateJWT():
    """ Verifies that JWT is valid. """
    auth_headers = request.headers.get('Authorization', '').split()
    if len(auth_headers) != 2:
        return None
    try:
        token = auth_headers[1]
        data = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms='HS256')
        user = User.query.filter(User.username.like((data['username']))).one_or_none()
        if user:
            return user
    except jwt.ExpiredSignatureError:
        return None
    except (jwt.InvalidTokenError, Exception) as e:
        return None
    return None

##############################################################################
# Listing Routes

@app.route('/listings')
def get_listings():
    """If search term included, gets filtered listings. Otherwise,
        gets all listings.
    """

    search = request.args.get('term')

    if not search: 
        listings = Listing.query.all()
    else: 
        listings = Listing.query.filter(Listing.address.ilike(f"%{search}%")).all()

    serialized = [listing.serialize() for listing in listings]
    return (jsonify(listings=serialized))


@app.route('/listings', methods=["POST"])
def add_listing():
    """Handle add listing.

    Create new listing and add to DB.
    """
    
    user = authenticateJWT()
    if user:
        img_urls = []
        for key in request.files:
            file = request.files.get(key)
            output = upload_file_to_s3(file, S3_BUCKET)
            img_urls.append(output)
        # print(img_urls)
        # breakpoint()
        # file = request.files["photo"]

        # output = upload_file_to_s3(file, S3_BUCKET)
        # photos = str(output)
        # print("PHOTOS AFTER UPLOAD", photos)

        title = request.form.getlist("title")[0]
        price = request.form.getlist("price")[0]
        address = request.form.getlist("address")[0]
        details = request.form.getlist("details")[0]

        new_listing = Listing(
            title=title,
            price=price,
            address=address,
            details=details,
            host_id=user.id,
        )

        db.session.add(new_listing)
        db.session.commit()

        for img_url in img_urls:
            new_listing_photo = ListingPhoto(
                listing_id=new_listing.id,
                url=img_url,
            )
            db.session.add(new_listing_photo)
            db.session.commit()
        
        serialized = new_listing.serialize()

        return (jsonify(listing=serialized), 201)

    return jsonify(error='Must be logged in'), 401


@app.route('/listings/<int:id>')
def get_listing(id): 
    """Gets listing by id."""

    listing = Listing.query.get_or_404(id)

    serialized = listing.serialize()

    return (jsonify(listing=serialized))


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

    duplicate_check = User.query.filter(User.username.like(username)).one_or_none()
    if duplicate_check:
        return jsonify(error='Username taken'), 400

    try: 
        user = User.signup(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
        token = createJWT(user)
        return jsonify(user=user.serialize(), token=token)

    except IntegrityError as error:
        return (jsonify(error=error))


# @app.route('/login', methods=["POST"])
# def login(): 
#     """Authenticates user and, if valid credentials, returns token."""

#     username = request.json["username"]
#     password = request.json["password"]

#     user = User.authenticate(username, password)

#     if user: 
#         token = createJWT(user)
#         return jsonify(user=user.serialize(), token=token)
#     else: 
#         return ("Invalid login", 400)



@app.route('/users')
def get_users():
    """If search term included, gets filtered users. Otherwise,
        gets all users.
    """

    search = request.args.get('q')

    if not search: 
        users = User.query.all()
        serialized = [user.serialize() for user in users]
        return (jsonify(users=serialized))
    else: 
        user = User.query.filter(User.username.like(f"{search}")).one_or_none()
        serialized = user.serialize()
        return (jsonify(user=serialized))

    

@app.route('/users/<int:id>')
def get_user(id): 
    """Gets user by id."""

    user = User.query.get_or_404(id)

    serialized = user.serialize()

    return (jsonify(user=serialized))

##############################################################################
# Message Routes

@app.route('/messages/<int:id>', methods=['POST'])
def send_message(id):
    """Send message to user with id."""

    text = request.json['message']
    curr_user = authenticateJWT()
    if curr_user:
        msg = Message(
            text=text,
            to_user_id=id,
            from_user_id=curr_user.id
        )

        db.session.add(msg)
        db.session.commit()

        return jsonify(msg=msg.serialize())
    
    else:
        return jsonify(error='Unauthorized'), 401

@app.route('/messages')
def get_messages():
    """Get all of current user's messages."""
    # breakpoint()
    curr_user = authenticateJWT()
    if curr_user:
        msgs = Message.query.filter((Message.from_user_id == curr_user.id) | (Message.to_user_id == curr_user.id)).all()
        serialized = [msg.serialize() for msg in msgs]
        return jsonify(msgs=serialized)
    
    else:
        return jsonify(error='Unauthorized'), 401

@app.route('/messages/<int:id>')
def get_conversion_with_user(id):
    """Get current user's messages to or from user with id."""

    curr_user = authenticateJWT()
    if curr_user:
        msgs = Message.query.filter(
            (
                ((Message.from_user_id == curr_user.id) | (Message.to_user_id == curr_user.id))
                &
                ((Message.from_user_id == id) | (Message.to_user_id == id)))
            ).order_by("timestamp").all()
        serialized = [msg.serialize() for msg in msgs]
        return jsonify(msgs=serialized)
    
    else:
        return jsonify(error='Unauthorized'), 401