from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import session
from flask import logging
from passlib.hash import sha256_crypt
import mysql.connector
from mysql.connector import Error

import psycopg2 as pg2

import os, sys, time

# Import from own library
from decorators import is_logged_in
from decorators import is_not_logged_in
from decorators import has_aadhar
from decorators import has_driving

# Importing Forms
from forms import RegisterForm

# Importing database credentials
from flask_sqlalchemy import SQLAlchemy
from database_credentials import credentials

import db_models

# app.config['SECRET_KEY'] = "747b60ab7ef6e02cf56da6503adae95198fa6dad"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://arsalan:123@localhost/carpool'

app = Flask(__name__)

app.config['SECRET_KEY'] = "747b60ab7ef6e02cf56da6503adae95198fa6dad"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://arsalan:123@localhost/carpool'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

db_models.db.init_app(app)



startup_duration = 0
timeout_s = 10
start_time = time.time()
last_exception = None
conn = None

# while startup_duration < timeout_s:
#     try:
#         startup_duration = time.time() - start_time
#         # Initialize the SQLAlchemy extension
#         db = SQLAlchemy(app)

#         break
#     except Exception as e:
#         print(f'Elapsed: {int(startup_duration)} / {timeout_s} seconds')
#         last_exception = e
#         time.sleep(1)

# if startup_duration >= timeout_s:
#     print(f'Could not initialize the database within {timeout_s} seconds - {last_exception}')
#     exit()

# connection_status = ('Not connected', 'Connected')[conn.close == 0]
# print(f'Connection status: {connection_status}\n\n', file=sys.stderr, flush=True)



# Index
@app.route('/')
def index():
	return render_template('home.html')

# Terms
@app.route('/about')
def about():
	return render_template('about.html')

# User Register
@app.route('/register', methods=['GET','POST'])
@is_not_logged_in
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		# User General Details
		fname = form.fname.data
		lname = form.lname.data
		contactNo = form.contactNo.data
		alternateContactNo = ""
		emailID = form.emailID.data
		gender = str(form.gender.data).upper()
		driving = form.driving.data
		aadhar = form.aadhar.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# User Address
		addLine1 = form.addLine1.data
		addLine2 = form.addLine2.data
		colony = ""
		city = form.city.data
		state = form.state.data

		# Create cursor
		# cur = conn.cursor()

		try:
			if len(aadhar)==0 and len(driving)==0:
				print("======1111====")
				# Add User into Database
				new_user = db_models.User(
					fname=fname,
					lname=lname,
					contactNo=contactNo,
					alternateContactNo=alternateContactNo,
					email=emailID,
					password=password,
					addLine1=addLine1,
					addLine2=addLine2,
					colony=colony,
					city=city,
					state=state,
					gender=gender,
					userStatus="NONE"
        		)
			elif len(aadhar)!=0 and len(driving)==0:
				print("======222=====")
				# Add User into Database
				new_user = db_models.User(
					fname=fname,
					lname=lname,
					contactNo=contactNo,
					alternateContactNo=alternateContactNo,
					email=emailID,
					password=password,
					addLine1=addLine1,
					addLine2=addLine2,
					colony=colony,
					city=city,
					state=state,
					aadhar=aadhar,
					gender=gender,
					userStatus="AADHAR"
				)
			elif len(aadhar)==0 and len(driving)!=0:
				print("======333=====")
				# Add User into Database
				new_user = db_models.User(
					fname=fname,
					lname=lname,
					contactNo=contactNo,
					alternateContactNo=alternateContactNo,
					email=emailID,
					password=password,
					addLine1=addLine1,
					addLine2=addLine2,
					colony=colony,
					city=city,
					state=state,
					gender=gender,
					driving=driving,
					userStatus="DRIVING"
				)
			elif len(aadhar)!=0 and len(driving)!=0:
				print("-----444---")
				# Add User into Database
				print(fname, lname, contactNo, alternateContactNo, emailID, password, addLine1, addLine2, colony, city, state, aadhar, gender, driving,"BOTH")
				new_user = db_models.User(
					fname=fname,
					lname=lname,
					contactNo=contactNo,
					alternateContactNo=alternateContactNo,
					email=emailID,
					password=password,
					addLine1=addLine1,
					addLine2=addLine2,
					colony=colony,
					city=city,
					state=state,
					aadhar=aadhar,
					gender=gender,
					driving=driving,
					userStatus="BOTH"
				)
			db_models.db.session.add(new_user)
			db_models.db.session.commit()

		except Exception as e:
			flash(e)
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('login'))

		flash('You are now Registered and can Log In','success')
		return redirect(url_for('login'))

	return render_template('register.html', form = form)

# User login
@app.route('/login', methods=['GET','POST'])
@is_not_logged_in
def login():
	if request.method == 'POST':
		# Get Form Fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor
		# cur = conn.cursor()

		try:
			print("======in try case------")
			# Get user by either Email or ContactNo
			if '@' in username:
				user = db_models.User.query.filter_by(email=username).first()
				print("======if case-----", user)
			else:
				user = db_models.User.query.filter_by(contactNo=username).first()
				print("======else case-----", user)


		except Exception as e:
			print("=====exception====")
			print(e)
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('login'))

		if user:
			# Compate Passwords
			if sha256_crypt.verify(password_candidate, user.password):
				session['logged_in'] = True
				session['userId'] = user.userId
				session['userStatus'] = user.userStatus
				session['userType'] = user.userType
				session['city'] = user.city
				
				msg = "Welcome {} {}".format(user.fname,user.lname)
				flash(msg,'success')

				return redirect(url_for('dashboard'))
			else:
				error = "Invalid login"
				return render_template('login.html', error = error)
			# Close connection
		else:
			error = "Username not found"
			return render_template('login.html', error = error)
	return render_template('login.html')

# Logout
@app.route('/loggout')
@is_logged_in
def logout():
	print('======inside here----')
	session.clear()
	flash('You are now Logged Out','success')
	print("======am i here----")
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')


# this part of code was buggy so some parts are removed

@app.route('/nearbyRides', methods=['GET','POST'])
@is_logged_in
@has_aadhar
def nearbyRides():
	if request.method == 'POST':
		print("======post method near by ride====")
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'DRIVING' or session['userStatus'] == 'NONE':
			flash('You Don\'t have PID!','warning')
			return redirect(url_for('dashboard'))
		
		RideId = request.form['rideId']
		print(RideId,"=====ride id===")

		# Create cursor
		# cur = conn.cursor()

		try:
			# Add User into Database
			# cur.execute("INSERT INTO ShareRequest(RideID, requestUserId) VALUES (%s, %s);", (RideId, session['userId']))
			new_share_request = db_models.ShareRequest(RideID=RideId, requestUserId=session['userId'])
			print(new_share_request,"====new share req====")
			db_models.db.session.add(new_share_request)
			db_models.db.session.commit()

		except Exception as e:
			print(e)
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		# # Comit to DB
		# conn.commit()

		# # Close connection
		# cur.close()

		
		flash('Your Request for Ride is sent to the user!','success')
		return redirect(url_for('dashboard'))
	

	if session['userStatus']=='REGISTERED' or session['userStatus'] == 'DRIVING' or session['userStatus'] == 'NONE':
		flash('You Don\'t have PID!','warning')
		return redirect(url_for('dashboard'))

	# Create cursor
	# cur = conn.cursor()
	print(session['userId'], file=sys.stderr)
	ui=session['userId']
	print("=====ui====",ui)
	try:
		print("=====i am here----")
		# Add User into Database
		# query_original = "SELECT * FROM Ride r, users u WHERE r.rideDate = DATE(NOW()) AND r.city = %s AND r.rideStatus = %s AND r.creatorUserId = u.userId",(session['city'],"PENDING")
		#query = "select * from (SELECT ridetime, fromlocation, tolocation, r.city, r.state, fname, lname, gender, seats, contactno, rideid, r.creatoruserid, u.userid  FROM users u, ride r where u.userid=r.creatoruserid and r.ridestatus='PENDING') as A where A.userid not in (%s);"(ui)
		# cur.execute("select * from (SELECT ridetime, fromlocation, tolocation, r.city, r.state, fname, lname, gender, seats, contactno, rideid, r.creatoruserid, u.userid, r.carstatus, r.message, ridedate  FROM users u, ride r where u.userid=r.creatoruserid and r.ridestatus='PENDING') as A where A.userid != %s",[ui])
		rides = (
        db_models.db.session.query(
            db_models.Ride.rideTime,
            db_models.Ride.fromLocation,
            db_models.Ride.toLocation,
            db_models.Ride.city,
            db_models.Ride.state,
            db_models.User.fname,
            db_models.User.lname,
            db_models.User.gender,
            db_models.Ride.seats,
            db_models.User.contactNo,
            db_models.Ride.RideId,
            db_models.Ride.creatorUserId,
            db_models.User.userId,
            db_models.Ride.carStatus,
            db_models.Ride.message,
            db_models.Ride.rideDate
        )
        .join(db_models.User, db_models.User.userId == db_models.Ride.creatorUserId)
        .filter(db_models.Ride.rideStatus == 'PENDING', db_models.User.userId != ui)
        .all()
    	)
	except Exception as e:
		print(e)
		db_models.db.session.rollback()  # Rollback the transaction in case of an error
		# conn.rollback()
		flash('Something went wrong','danger')
		return redirect(url_for('dashboard'))
	
	# rides = cur.fetchall()

	# # Comit to DB
	# conn.commit()

	# # Close connection
	# cur.close()

	print("=======testing =====", rides)

	if rides:
		print("======if rides exists====")
		return render_template('nearbyRides.html', rides = rides)
	else:
		flash('No Rides in your city!','warning')
		return redirect(url_for('dashboard'))

@app.route('/womennearbyRides', methods=['GET','POST'])
@is_logged_in
@has_aadhar
def womennearbyRides():
	if request.method == 'POST':
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'DRIVING' or session['userStatus'] == 'NONE':
			flash('You Don\'t have PID!','warning')
			return redirect(url_for('dashboard'))
		
		RideId = request.form['rideId']

		# Create cursor
		# cur = conn.cursor()

		try:
			# Add User into Database
			# cur.execute("INSERT INTO ShareRequest(RideID, requestUserId) VALUES (%s, %s);", (RideId, session['userId']))
			new_share_request = db_models.ShareRequest(RideID=RideId, requestUserId=session['userId'])
			db_models.db.session.add(new_share_request)
			db_models.db.session.commit()
		except:
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		
		# # Comit to DB
		# conn.commit()

		# # Close connection
		# cur.close()

		
		flash('Your Request for Ride is sent to the user!','success')
		return redirect(url_for('dashboard'))
	

	if session['userStatus']=='REGISTERED' or session['userStatus'] == 'DRIVING' or session['userStatus'] == 'NONE':
		flash('You Don\'t have PID!','warning')
		return redirect(url_for('dashboard'))

	# Create cursor
	# cur = conn.cursor()
	ui = session['userId']
	try:
		print("======women ride 101-----")
		# Add User into Database
		# query_original = "SELECT * FROM Ride r, users u WHERE r.rideDate = DATE(NOW()) AND r.city = %s AND r.rideStatus = %s AND r.creatorUserId = u.userId",(session['city'],"PENDING")
		#query = "SELECT * FROM Ride r, users u where u.gender = 'FEMALE' and r.creatoruserid != u.userid"
		# cur.execute("select * from (SELECT ridetime, fromlocation, tolocation, r.city, r.state, fname, lname, gender, seats, contactno, rideid, r.creatoruserid, u.userid, ridedate  FROM users u, ride r where gender = 'FEMALE' and u.userid=r.creatoruserid and r.ridestatus='PENDING') as A where A.userid != %s",[ui])
		rides = (
        db_models.db.session.query(
            db_models.Ride.rideTime,
            db_models.Ride.fromLocation,
            db_models.Ride.toLocation,
            db_models.Ride.city,
            db_models.Ride.state,
            db_models.User.fname,
            db_models.User.lname,
            db_models.User.gender,
            db_models.Ride.seats,
            db_models.User.contactNo,
            db_models.Ride.RideId,
            db_models.Ride.creatorUserId,
            db_models.User.userId,
            db_models.Ride.rideDate
        )
        .join(db_models.User, db_models.User.userId == db_models.Ride.creatorUserId)
        .filter(db_models.Ride.rideStatus == 'PENDING', db_models.User.gender == 'FEMALE', db_models.User.userId != ui)
        .all()
    	)
		print("=====women rides===")
	except:
		db_models.db.session.rollback()		
		flash('Something went wrong','danger')
		return redirect(url_for('dashboard'))
	
	# rides = cur.fetchall()

	# # Comit to DB
	# conn.commit()

	# # Close connection
	# cur.close()

	if rides:
		return render_template('womennearbyRides.html', rides = rides)
	else:
		flash('No Rides in your city with women drivers!','warning')
		return redirect(url_for('dashboard'))



@app.route('/rideRequests', methods=['GET','POST'])
@is_logged_in
@has_driving
def rideRequests():
	if request.method == 'POST':
		print("=======is this working-=----=-==-")
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
			flash('You Don\'t have Driving License!','warning')
			return redirect(url_for('dashboard'))
		
		rideId = request.form['rideId']
		
		# Create cursor
		# cur = conn.cursor()

		
		try:
			# fetching no of seats
			# cur.execute("select seats from Ride where RideId = %s",[rideId])
			seats = db_models.db.session.query(db_models.Ride.seats).filter_by(RideId=rideId).scalar()
			print("=====seats===", seats)
		except Exception as e:
			print(e,"=====exceptin one===")
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		# s = cur.fetchone()
		# seats = s[0]
		# cur.close()

		# cur = conn.cursor()
       
		
		try:
			print("======try case 2====")
			# fetching the request creater ID
			# cur.execute("select requestuserid from sharerequest s,ride r where s.rideid=r.rideid")
			requestUser = db_models.db.session.query(db_models.ShareRequest.requestUserId).join(db_models.Ride, db_models.ShareRequest.RideID == db_models.Ride.RideId).all()
			print("===requestUser===", requestUser)
		except:
			print("======exception===",e)
			db_models.db.session.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		# requestUser= cur.fetchall()
		requestUserIds=requestUser
		

	
		
		print(rideId,file=sys.stderr)
		print(session['userId'],file=sys.stderr)
		print(requestUserIds,file=sys.stderr)
		if seats - 1 > 0:
			try:
				# Update User Details into the Database
				db_models.db.session.query(db_models.Ride).filter_by(RideId=rideId).update({'seats': seats - 1})
				db_models.db.session.commit()

				# cur.execute("UPDATE Ride SET seats = %s",[seats-1])
				for requestUserId in requestUserIds:
					# cur.execute("INSERT INTO passenger(rideid, creatoruserid, requestuserid) VALUES (%s,%s,%s);", (rideId, session['userId'] ,requestUserId))
					new_passenger = db_models.Passenger(RideID=rideId, creatorUserId=session['userId'], requestUserId=requestUserId[0])
					db_models.db.session.add(new_passenger)
					# cur.execute("delete from sharerequest s where s.requestUserId in (select s.requestUserId from sharerequest s,passenger p where s.requestUserId=p.requestUserId )")
					db_models.db.session.query(db_models.ShareRequest).filter(db_models.ShareRequest.requestUserId == requestUserId[0]).delete()
			except Exception as e:
				print(e)
				db_models.db.session.rollback()
				flash('Something went wrong','danger')
				return redirect(url_for('dashboard'))
		else:
			try:
				# Update User Details into the Database
				# cur.execute("UPDATE Ride SET seats = %s,rideStatus = 'DONE'",[seats-1])
				db_models.db.session.query(db_models.Ride).filter_by(RideId=rideId).update({'seats': seats - 1, 'rideStatus': 'DONE'})

				for requestUserId in requestUserIds:
					# cur.execute("INSERT INTO passenger(rideid, creatoruserid, requestuserid) VALUES (%s,%s,%s);", (rideId, session['userId'] ,requestUserId))
					new_passenger = db_models.Passenger(RideID=rideId, creatorUserId=session['userId'], requestUserId=requestUserId[0])
					db_models.db.session.add(new_passenger)
					print("======execution here=====")
					# cur.execute("delete from sharerequest s where s.requestUserId in (select s.requestUserId from sharerequest s,passenger p where s.requestUserId=p.requestUserId )")
					db_models.db.session.query(db_models.ShareRequest).filter(db_models.ShareRequest.requestUserId.in_(
            			db_models.db.session.query(db_models.Passenger.requestUserId).filter(db_models.Passenger.RideID == rideId))).delete(synchronize_session=False)
					db_models.db.session.commit()

			except Exception as e:
				print(e)
				db_models.db.session.rollback()
				flash('Something went wrong','danger')
				return redirect(url_for('dashboard'))

		# # Comit to DB
		# conn.commit()

		# # Close connection
		# cur.close()

		flash('Request accepted for the ride','success')
		return redirect(url_for('dashboard'))

	if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
			flash('You Don\'t have Driving License!','warning')
			return redirect(url_for('dashboard'))

	# Create cursor
	# cur = conn.cursor()

	try:
		print("=====ride request====")
		# Fetch all the ShareRequests and Details
		results = (
        	db_models.db.session.query(
				db_models.Ride.rideTime,
				db_models.Ride.fromLocation,
				db_models.Ride.toLocation,
				db_models.Ride.city,
				db_models.Ride.state,
				db_models.User.fname,
				db_models.User.lname,
				db_models.User.gender,
				db_models.Ride.seats,
				db_models.User.contactNo,
				db_models.Ride.RideId,
				db_models.Ride.creatorUserId,
				db_models.User.userId,
				db_models.Ride.rideDate,
			)
        	.join(db_models.ShareRequest, db_models.Ride.RideId == db_models.ShareRequest.RideID)
        	.join(db_models.User, db_models.ShareRequest.requestUserId == db_models.User.userId)
        	.filter(
            	db_models.Ride.rideStatus == 'PENDING',
            	db_models.Ride.creatorUserId == session['userId'])
        	.all()
    	)
	except Exception as e:
		print(e)
		db_models.db.session.rollback()
		flash('Something went wrong','danger')
		return redirect(url_for('dashboard'))

	rideRequests = results

	# Comit to DB
	db_models.db.session.commit()

	# Close connection
	# cur.close()

	if rideRequests:
		return render_template('rideRequests.html', rideRequests = rideRequests)
	else:
		flash('No Requests for Your Ride!','warning')
		return redirect(url_for('dashboard'))

	return render_template('rideRequests.html')

@app.route('/acceptedRides', methods=['GET','POST'])
@is_logged_in
@has_driving
def acceptedRides():
	if request.method == 'POST':
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
			flash('You Don\'t have Driving License!','warning')
			return redirect(url_for('dashboard'))
		
		rideId = request.form['rideId']
		
		# Create cursor
		cur = conn.cursor()

		
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
				flash('You Don\'t have Driving License!','warning')
				return redirect(url_for('dashboard'))

	# Create cursor
	cur = conn.cursor()

	try:
		# Fetch all the ShareRequests and Details
		#cur.execute("SELECT * FROM passenger p, ride r, users u WHERE r.RideId = p.rideid AND p.creatoruserid = %s AND p.requestUserId = u.userId",[session['userId']])
		cur.execute("SELECT DISTINCT r.ridedate, r.ridetime,r.fromlocation, r.tolocation, r.city, r.state,  u.fname, u.lname, u.gender, u.contactno, p.rideid FROM passenger p, ride r, users u WHERE r.RideId = p.rideid AND p.creatoruserid = %s AND p.requestUserId = u.userId",[session['userId']])

	except:
		conn.rollback()
		flash('Something went wrong','danger')
		return redirect(url_for('dashboard'))

	acceptedRides = cur.fetchall()

	# Comit to DB
	conn.commit()

	# Close connection
	cur.close()

	if rideRequests:
		return render_template('acceptedRides.html', acceptedRides = acceptedRides)
	else:
		flash('No Passengers for Your Ride!','warning')
		return redirect(url_for('dashboard'))

	return render_template('accepetedRides.html')




@app.route('/shareRide', methods=['GET','POST'])
@is_logged_in
@has_driving
def shareRide():
	if request.method == 'POST':
		if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
			flash('You Don\'t have Driving License!','warning')
			return redirect(url_for('dashboard'))

		rideDate = request.form['rideDate']	
		rideTime = request.form['rideTime']
		fromLocation = request.form['fromLocation']
		toLocation = request.form['toLocation']
		seats = request.form['seats']			
		city = request.form['city']
		state = request.form['state']
		carStatus = request.form['carState']
		message = request.form['message']

		# Create cursor
		cur = conn.cursor()

		try:
			# Add Ride into the Database
			cur.execute("INSERT INTO Ride(creatorUserId, rideDate, rideTime, fromLocation, toLocation, seats, city, state,carStatus,message) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s)", (session['userId'], rideDate, rideTime, fromLocation, toLocation, seats, city, state,carStatus,message))
		except:
			conn.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		# Comit to DB
		conn.commit()

		# Close connection
		cur.close()

		flash('Your ride is shared people around you can now send you request for your ride','success')
		return redirect(url_for('dashboard'))
	
	if session['userStatus']=='REGISTERED' or session['userStatus'] == 'AADHAR' or session['userStatus'] == 'NONE':
		flash('You Don\'t have Driving License!','warning')
		return redirect(url_for('dashboard'))
	return render_template('shareRide.html')


@app.route('/settings', methods=['GET','POST'])
@is_logged_in
def settings():
	if request.method == 'POST':
		contactNo = request.form['contactNo']
		alternateContactNo = ""
		email = request.form['email']
		gender = request.form['gender']
		driving = request.form['driving']
		aadharID = request.form['aadharID']
		addLine1 = request.form['addLine1']
		addLine2 = request.form['addLine2']
		colony = ""
		city = request.form['city']
		state = request.form['state']


		if len(aadharID)==0 and len(driving)==0:
			userStatus = "NONE"
		elif len(aadharID)!=0 and len(driving)==0:
			userStatus = "AADHAR"
		elif len(aadharID)==0 and len(driving)!=0:
			userStatus = "DRIVING"
		elif len(aadharID)!=0 and len(driving)!=0:
			userStatus = "BOTH"

		# Create cursor
		cur = conn.cursor()

		try:
			# Update User Details into the Database
			cur.execute("UPDATE users SET contactNo=%s, alternateContactNo=%s, email=%s, gender = %s, driving=%s, aadhar=%s, addLine1=%s, addLine2= %s, colony= %s, city=%s, state = %s, userStatus = %s WHERE userId = %s",(contactNo, alternateContactNo, email, gender, driving, aadharID, addLine1, addLine2, colony, city, state, userStatus, session['userId']))
		except:
			conn.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('dashboard'))

		session['userStatus'] = userStatus

		# Comit to DB
		conn.commit()

		# Close connection
		cur.close()


		flash('Profile Updated Successfully','success')
		return redirect(url_for('dashboard'))

	# Create cursor
	cur = conn.cursor()

	try:
		# Fetch User Details from the Database
		cur.execute("SELECT * FROM users WHERE userId = %s", [session['userId']])
	except:
		conn.rollback()
		flash('Something went wrong','danger')
		return redirect(url_for('dashboard'))

	userData = cur.fetchone()

	# Close connection
	cur.close()

	if userData:
		return render_template('settings.html', userData = userData)
	else:
		return "Something went wrong"

if __name__ == '__main__':
	app.secret_key = 'secret123'
	port = int(os.environ.get("PORT",8000))
	app.run(host='0.0.0.0', port=port, debug=True)