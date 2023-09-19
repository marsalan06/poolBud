
# db = SQLAlchemy()
# from app import db
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    userId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    gender = db.Column(db.String(50))
    driving = db.Column(db.String(50), unique=True)
    aadhar = db.Column(db.String(50), unique=True)
    contactNo = db.Column(db.String(30), unique=True)
    alternateContactNo = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    registerDate = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    addLine1 = db.Column(db.String(150))
    addLine2 = db.Column(db.String(150))
    colony = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    userStatus = db.Column(db.String(50), default='LOGGEDIN')
    userType = db.Column(db.String(50), default='CUSTOMER')

    def __init__(self, fname, lname, gender, driving, aadhar, contactNo, email, password,
                 addLine1, addLine2, colony, city, state, userStatus='LOGGEDIN', userType='CUSTOMER'):
        self.fname = fname
        self.lname = lname
        self.gender = gender
        self.driving = driving
        self.aadhar = aadhar
        self.contactNo = contactNo
        self.email = email
        self.password = password
        self.addLine1 = addLine1
        self.addLine2 = addLine2
        self.colony = colony
        self.city = city
        self.state = state
        self.userStatus = userStatus
        self.userType = userType

    def __repr__(self):
        return f'<User(userId={self.userId}, fname={self.fname}, email={self.email})>'


class Ride(db.Model):
    __tablename__ = 'Ride'
    
    RideId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    creatorUserId = db.Column(db.Integer)
    rideDate = db.Column(db.DATE)
    rideTime = db.Column(db.TIME)
    rideStatus = db.Column(db.String(50), default='PENDING')
    fromLocation = db.Column(db.String(100))
    toLocation = db.Column(db.String(100))
    seats = db.Column(db.Integer)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    carStatus = db.Column(db.String(256))
    message = db.Column(db.String(256))

    def __init__(self, creatorUserId, rideDate, rideTime, fromLocation, toLocation, seats,
                 city, state, carStatus='', message='', rideStatus='PENDING'):
        self.creatorUserId = creatorUserId
        self.rideDate = rideDate
        self.rideTime = rideTime
        self.fromLocation = fromLocation
        self.toLocation = toLocation
        self.seats = seats
        self.city = city
        self.state = state
        self.carStatus = carStatus
        self.message = message
        self.rideStatus = rideStatus

    def __repr__(self):
        return f'<Ride(RideId={self.RideId}, fromLocation={self.fromLocation}, toLocation={self.toLocation})>'


class ShareRequest(db.Model):
    __tablename__ = 'ShareRequest'
    
    RequestID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    RideID = db.Column(db.Integer)
    requestUserId = db.Column(db.Integer)

    def __init__(self, RideID, requestUserId):
        self.RideID = RideID
        self.requestUserId = requestUserId

    def __repr__(self):
        return f'<ShareRequest(RequestID={self.RequestID}, RideID={self.RideID}, requestUserId={self.requestUserId})>'


class Passenger(db.Model):
    __tablename__ = 'Passenger'
    
    PassengerID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    RideID = db.Column(db.Integer)
    creatorUserId = db.Column(db.Integer)
    requestUserId = db.Column(db.Integer)

    def __init__(self, RideID, creatorUserId, requestUserId):
        self.RideID = RideID
        self.creatorUserId = creatorUserId
        self.requestUserId = requestUserId

    def __repr__(self):
        return f'<Passenger(PassengerID={self.PassengerID}, RideID={self.RideID}, requestUserId={self.requestUserId})>'
