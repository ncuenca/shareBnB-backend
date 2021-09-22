import os

from flask import Flask, request, jsonify
from models import Message, db, connect_db, User, Listing, ListingPhoto
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
# from werkzeug.security import secure_filename
from helpers import upload_file_to_s3
from my_secrets import S3_SMALL_BUCKET, S3_LARGE_BUCKET
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

def createJWT(user):
    """ Given user instance, creates and returns JWT token with username and
        admin in payload.
    """

    payload = { 'username':user.username, 'is_admin':user.is_admin }
    token = jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
    return token

def authenticateJWT():
    """Verifies that JWT is valid. Returns user information if valid or empty
        dictionary if invalid.

        If valid, returns:
            user: {id, username, first_name, last_name, email, phone}
    """

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

@app.route('/users', methods=["POST"])
def sign_up(): 
    """Handles user sign up. If valid form data and no duplicate, returns
        serialized user information and token. Otherwise, error.
    
        Accepts: 
            { username, password, first_name, last_name, email, phone }

        Returns: 
            {
                user: {username, first_name, last_name, email, phone},
                token: "token"
            }
    """

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

@app.route('/login', methods=['POST'])
def login():
    """If valid credentials presented in JSON, returns token, otherwise 401 error.

        Accepts: {username, password}
    """

    username = request.json['username']
    password = request.json['password']
    
    user = User.authenticate(username, password)
    if user:
        token = createJWT(user)
        return (jsonify(user=user.serialize(),token=token))
    return jsonify(error='Invalid login'), 401


##############################################################################
# Listing Routes

@app.route('/listings')
def get_listings():
    """If search term included, gets filtered listings. Otherwise,
        gets all listings.

        Returns: listings: [{id, title, price, details, address, host_id, photos}, ...]
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
    """Creates new listing and adds to DB. Uploads photos to AWS S3 and adds to
        listing photos table. Returns serialized listing in JSON.

        Returns: 
            listing: {id, title, price, details, address, host_id, photos}
            where photos is: 
                [photo_url, photo_url, photo_url, ...]
    """
    
    user = authenticateJWT()
    if user:
        small_img_urls = []
        large_img_urls = []
        for key in request.files:
            file = request.files.get(key)
            small_img_output = upload_file_to_s3(file, S3_SMALL_BUCKET)
            small_img_urls.append(small_img_output)
            large_img_output = upload_file_to_s3(file, S3_LARGE_BUCKET)
            large_img_urls.append(large_img_output)

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

        for i in range(len(small_img_urls)):
            new_listing_photo = ListingPhoto(
                listing_id=new_listing.id,
                small_photo_url=small_img_urls[i],
                large_photo_url=large_img_urls[i],
            )
            db.session.add(new_listing_photo)
            db.session.commit()
        
        serialized = new_listing.serialize()

        return (jsonify(listing=serialized), 201)

    return jsonify(error='Must be logged in'), 401


@app.route('/listings/<int:id>')
def get_listing(id): 
    """Gets listing by id. Returns serialized listing details in JSON.

        Returns: 
            listing: {id, title, price, details, address, host_id, photos}
    """

    listing = Listing.query.get_or_404(id)

    serialized = listing.serialize()

    return (jsonify(listing=serialized))


##############################################################################
# User Routes

@app.route('/users')
def get_users():
    """If search term included, gets filtered users. Otherwise,
        gets all users. Returns list of serialized users in JSON.

        Accepts: 
            q: "term" (optional)
        
        Returns: 
            users: [{username, first_name, last_name, email, phone}, ...]
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
    """Gets user by id. If found, returns serialized user information in JSON.
        Otherwise, 404.
    
        Returns: 
            user: {username, first_name, last_name, email, phone}
    """

    user = User.query.get_or_404(id)

    serialized = user.serialize()

    return (jsonify(user=serialized))

##############################################################################
# Message Routes

@app.route('/messages/<int:id>', methods=['POST'])
def send_message(id):
    """Send message from current user to user of id in url params. If valid
        token, returns serialized message details in JSON.

        Returns: 
            msg: {id, text, timestamp, to_user_id, to_user, from_user_id, from_user}
            Where to_user and from_user is: 
                {username, first_name, last_name, email, phone}
    """

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
    """Get all of current user's messages. If valid token, returns serialized
        list of all messages.

        Returns: 
            msgs: [{id, text, timestamp, to_user_id, to_user, from_user_id, from_user}, ...]
            Where to_user and from_user is: 
                {username, first_name, last_name, email, phone}
    """

    curr_user = authenticateJWT()
    if curr_user:
        msgs = Message.query.filter((Message.from_user_id == curr_user.id) | (Message.to_user_id == curr_user.id)).all()
        serialized = [msg.serialize() for msg in msgs]
        return jsonify(msgs=serialized)
    
    else:
        return jsonify(error='Unauthorized'), 401

@app.route('/messages/<int:id>')
def get_conversion_with_user(id):
    """Get current user's messages to or from user of id in url params. If
        valid token, returns serialized list of messages.

        Returns: 
            msgs: [{id, text, timestamp, to_user_id, to_user, from_user_id, from_user}, ...]
            Where to_user and from_user is: 
                {username, first_name, last_name, email, phone}
    """

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