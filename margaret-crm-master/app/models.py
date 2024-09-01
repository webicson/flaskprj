from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import jwt
from app import db, login
import json
from json import JSONEncoder
from flask import jsonify, json
from app.rivhit_api import rivhit_customer_list, rivhit_add_new_customer
from ast import literal_eval


# Many To Many
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )  # Since this is an auxiliary table that has no data other than the foreign keys, I created it without an associated model class.

activedids = db.Table('activedids',
    db.Column('did_id', db.Integer, db.ForeignKey('dids.id'), primary_key=True),
    db.Column('customer_id', db.Integer, db.ForeignKey('customers.id'), primary_key=True),
)

class Activations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    did_id = db.Column(db.Integer, db.ForeignKey('dids.id'),  nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    time_start = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    time_end = db.Column(db.DateTime, index=True)
    # did = db.relationship('Dids', backref='activations', lazy='dynamic')

    def is_active(self):
        return self.time_end is not None

    def is_available(self):
        return self.time_end is None



class Dids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(255), unique = True, nullable = False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'),  nullable = False)  # one to many
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))  # one to many
    type = db.Column(db.Integer, db.ForeignKey('didtypes.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'),  nullable = False)  # one to many
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # activations = db.relationship('Activations', backref='dids', lazy='dynamic')

    def is_active(self):
        a = db.session.query(
            Dids, Activations
        ).join(Activations
               ).filter(self.id == Activations.did_id).all()

        for aa in a:
            if aa.Activations.time_end is None:
                return True

        return False

    def activation_times(self):
        a = db.session.query(
            Dids, Activations
        ).join(Activations
               ).filter(self.id == Activations.did_id).all()
        return len(a)

    def is_available(self):
        if self.activations.size == 0:
            return False


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    followed = db.relationship(
        # I'm using the db.relationship function to define the relationship in the model class.# This relationship links User instances to other User instances
        'User',
        # 'User' is the right side entity of the relationship (the left side entity is the parent class). - The user been followed
        secondary=followers,
        # secondary configures the association table that is used for this relationship, which I defined right above this class.
        primaryjoin=(followers.c.follower_id == id),
        # primaryjoin indicates the condition that links the left side entity (the follower user) with the association table. The join condition for the left side of the relationship is the user ID matching the follower_id field of the association table. The followers.c.follower_id expression references the follower_id column of the association table.
        secondaryjoin=(followers.c.followed_id == id),
        # secondaryjoin indicates the condition that links the right side entity (the followed user) with the association table. This condition is similar to the one for primaryjoin, with the only difference that now I'm using followed_id, which is the other foreign key in the association table.
        backref=db.backref('followers', lazy='dynamic'),
        # backref defines how this relationship will be accessed from the right side entity. From the left side, the relationship is named followed, so from the right side I am going to use the name followers to represent all the left side users that are linked to the target user in the right side.
        # The additional lazy argument indicates the execution mode for this query. A mode of dynamic sets up the query to not run until specifically requested, which is also how I set up the posts one-to-many relationship.
        lazy='dynamic')  # lazy is similar to the parameter of the same name in the backref, but this one applies to the left side query instead of the right side.

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user): # is_following() looks for items in the association table that have the left side foreign key set to the self user, and the right side set to the user argument. The query is terminated with a count() method, which returns the number of results. The result of this query is going to be 0 or 1, so checking for the count being 1 or greater than 0 is actually equivalent.
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0  # The filter() method that I'm using here is similar, but lower level, as it can include arbitrary filtering conditions, unlike filter_by() which can only check for equality to a constant value.
    # he is_following() method issues a query on the followed relationship to check if a link between two users already exists.

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600): # The get_reset_password_token() function generates a JWT token as a string. Note that the decode('utf-8') is necessary because the jwt.encode() function returns the token as a byte sequence, but in the application it is more convenient to have the token as a string.
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')



    @staticmethod # The verify_reset_password_token() is a static method, which means that it can be invoked directly from the class.  A static method is similar to a class method, with the only difference that static methods do not receive the class as a first argument.
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password'] # This method takes a token and attempts to decode it by invoking PyJWT's jwt.decode() function. If the token cannot be validated or is expired, an exception will be raised, and in that case I catch it to prevent the error, and then return None to the caller.
        except:
            return
        return User.query.get(id) #  If the token is valid, then the value of the reset_password key from the token's payload is the ID of the user, so I can load the user and return it.

class Post(db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # one to many
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    name = db.Column(db.String(255),unique=True)
    phonecodeprefix = db.Column(db.String(10))
    regions = db.relationship('Regions', backref='country', lazy=True)
    cities = db.relationship('Cities', backref='country', lazy=True)
    dids = db.relationship('Dids', backref='country', lazy=True)

class NexmoSms(db.Model): # Inbound Message From Nexmo
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    # Possible values are:
    # text - standard text
    # unicode - a text message that contains Unicode characters
    # binary - a binary message
    to = db.Column(db.String(50))#The phone number that the message was sent to. This is your virtual number.
    msisdn = db.Column(db.String(50)) # The phone number that this inbound message was sent from.
    messageId = db.Column(db.String(50)) # Nexmo's unique identifier for this message.
    messageTimestamp = db.Column(db.String(50)) #The UTC±00:00 time when Nexmo started to push this inbound message to your webhook endpoint, in the following format: YYYY-MM-DD HH:MM:SS.
    timestamp = db.Column(db.String(50)) # The unix timestamp representation of message-timestamp.
    nonce = db.Column(db.String(50))
    # A random string that adds an extra element of unpredictability into the signature for the request. You use the nonce and timestamp parameters with your shared secret to calculate and validate the signature for inbound messages.
    # If your messages are signed
    #
    # For messages of type text or unicode
    # If the type is text or unicode, the following properties appear in the request to your webhook endpoint.
    text = db.Column(db.String(100000)) #The message body for this inbound message.
    keyword = db.Column(db.String(250)) #The first word in the message body. This is typically used with short codes.
    #
    # For messages of type binary
    # If the type is binary, the following properties appear in the request to your webhook endpoint.
    data = db.Column(db.String(100000)) #The content of this message
    udh = db.Column(db.String(100000)) #The hex encoded user data header
    #
    # For concatenated inbound messages
    concat = db.Column(db.String(250)) #true
    concatRef =db.Column(db.String(250)) #The transaction reference. All parts of this message share this concat-ref.
    concatTotal = db.Column(db.String(250)) # The number of parts in this concatenated message.
    concatPart = db.Column(db.String(250)) # The number of this part in the message. The first part of the message is 1.


class Regions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    code = db.Column(db.String(10))
    phonecodeprefix = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))  # one to many
    cities = db.relationship('Cities', backref='region', lazy=True)

class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phonecodeprefix = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))  # one to many
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))  # one to many
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    dids = db.relationship('Dids', backref='cities', lazy=True)

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    symbol = db.Column(db.String(10))
    country = db.Column(db.String(255))

class Vendors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    short = db.Column(db.String(255))

class Didtypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    rivhit_id = db.Column(db.Integer, unique=True)

    activedids = db.relationship(
        'Dids',
        secondary=activedids)
    def add_did(self, did):
        # if not self.is_following(did):
        self.activedids.append(did)

class Rivhit_customer:
    def __init__(self,
                 last_name,
                 first_name = "",
                 address = "",
                 city ="",
                 phone="",
                 id_number = 0,
                 email = "",customer_id = 0):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.city = city
        self.phone = phone
        self.id_number = id_number
        self.customer_id = customer_id

        # self.vat_number = vat_number

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def printit(self):
        # data = literal_eval(json.dumps(self.__dict__))
        data = json.loads(json.dumps(self.__dict__))
        # data = ast.literal_eval(MyEncoder().encode(self))
        # data_2 = {"last_name": self.last_name, "first_name": self.first_name}
        # data_4 = self.toJSON()
        # # return data
        return data

    def add_to_db(self):
        if not self.is_in_db():
            customer = Customers(first_name=self.first_name, last_name = self.last_name, email=self.email, rivhit_id = self.customer_id)
            db.session.add(customer)
            db.session.commit()

    def is_in_db(self):
        customer = Customers.query.filter_by(rivhit_id=self.customer_id).first()
        if customer is not None:
            return True
        else:
            return False

    def add_to_rivhit(self):
        data = json.loads(json.dumps(self.__dict__))
        rivhit_id = rivhit_add_new_customer(data)
        self.customer_id = rivhit_id
        return rivhit_id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class A2b_account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    account_username = db.Column(db.String(120), index=True)
    account_password = db.Column(db.String(120), index=True)
    forword_sms_to_phone_s = db.relationship('Forword_sms_to_phone', backref='A2b_account', lazy=True)


class Outbuond_number(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    phone_number = db.Column(db.String(120), index=True)

class Outbuond_email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    email= db.Column(db.String(120), index=True)

class Forword_sms_to_phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msisdn = db.Column(db.String(120), index=True)
    a2b_account_id = db.Column(db.Integer, db.ForeignKey('a2b_account.id'), nullable=False)
    outbuond_number_id = db.Column(db.Integer, db.ForeignKey('outbuond_number.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    time_start = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    time_end = db.Column(db.DateTime, index=True)

    def is_active(self):
        return self.time_end is not None

    def is_available(self):
        return self.time_end is None

## sms end ###