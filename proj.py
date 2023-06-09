#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	cursor = conn.cursor()
	query = 'SELECT * FROM public_info'
	cursor.execute(query)
	info = cursor.fetchall()
	cursor.close()
	return render_template('index.html', flights=info)


#flight search
@app.route('/flight_search')
def flight_search():
	if (session):
		return render_template('flight_search.html', loggedin=True)
	else:
		return render_template('flight_search.html', loggedin=False)
@app.route('/search', methods=['GET', 'POST'])
def search():
	search_type = request.form['search_type']
	if (search_type == 'city'):
		source_city = request.form['source']
		destination_city = request.form['destination']
	else:
		source_airport = request.form['source']
		destination_airport = request.form['destination']
	depart_date = request.form['departure_date']
	return_date = request.form.get('return_date', None)

	cursor = conn.cursor()
	if (search_type == 'city'):
		if (return_date):
			query = 'SELECT airline_name, flight_number, departure_date, departure_time, arrival_date, arrival_time, flight_status FROM Flight where departure_airport in (select airport_code from Airport where city=%s) and arrival_airport in (select airport_code from Airport where city=%s) and departure_date=%s'
			cursor.execute(query, (source_city, destination_city, depart_date))
			depart_flights = cursor.fetchall()
			cursor.execute(query, (destination_city, source_city, return_date))
			return_flights = cursor.fetchall()
		else:
			query = 'SELECT airline_name, flight_number, departure_date, departure_time, arrival_date, arrival_time, flight_status FROM Flight where departure_airport in (select airport_code from Airport where city=%s) and arrival_airport in (select airport_code from Airport where city=%s) and departure_date=%s'
			cursor.execute(query, (source_city, destination_city, depart_date))
			depart_flights = cursor.fetchall()
	else:
		if (return_date):
			query = 'SELECT airline_name, flight_number, departure_date, departure_time, arrival_date, arrival_time, flight_status FROM Flight where departure_airport=%s and arrival_airport=%s and departure_date=%s'
			cursor.execute(query, (source_airport, destination_airport, depart_date))
			depart_flights = cursor.fetchall()
			cursor.execute(query, (destination_airport, source_airport, return_date))
			return_flights = cursor.fetchall()
		else:
			query = 'SELECT airline_name, flight_number, departure_date, departure_time, arrival_date, arrival_time, flight_status FROM Flight where departure_airport=%s and arrival_airport=%s and departure_date=%s'
			cursor.execute(query, (source_airport, destination_airport, depart_date))
			depart_flights = cursor.fetchall()
	cursor.close()
	if (return_date):
		return render_template('search_result.html', departs=depart_flights, returns=return_flights)
	else:
		return render_template('search_result.html', departs=depart_flights)


#customer login
@app.route('/customer_login')
def customer_login():
	return render_template('customer_login.html')
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	email = request.form['email']
	customer_password = request.form['customer_password']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s and customer_password = %s'
	cursor.execute(query, (email, customer_password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#set user log in status
		cursor = conn.cursor()
		query = "UPDATE Customer SET log_in_status='online' WHERE email='" + email + "';"
		print(query)
		cursor.execute(query)
		conn.commit()
		cursor.close()
		#creates a session for the the user
		#session is a built in
		session['customer'] = email
		return redirect(url_for('customer_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid email or wrong password'
		return render_template('customer_login.html', error=error)


#customer register
@app.route('/customer_register')
def customer_register():
	return render_template('customer_register.html')
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	#email, customer_password, first_name, last_name, building_name, street_name, apt_number, city, state, zipcode, passport_number, passport_country, date_of_birth, log_in_status
	email = request.form['email']
	customer_password = request.form['customer_password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	phone_number = request.form['phone_number']
	building_name = request.form['building_name']
	street_name = request.form['street_name']
	apt_number = request.form['apt_number']
	city = request.form['city']
	state = request.form['state']
	zipcode = int(request.form['zipcode'])
	passport_number = request.form['passport_number']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']
	log_in_status = 'online'
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customer_register.html', error = error)
	else:
		#instruction to add to customer
		ins = "INSERT INTO Customer VALUES("
		for each in [email, customer_password, first_name, last_name]:
			ins = ins + "'" + each + "', "
		for each in [building_name, street_name, apt_number, city, state]:
			if each == '' or each:
				ins = ins + "null, "
			elif isinstance(each, int):
				ins = ins + str(each) + ", "
			else:
				ins = ins + "'" + str(each) + "', "
		ins = ins + str(zipcode) + ", "
		for each in [passport_number, passport_country, date_of_birth]:
			if each == '' or each:
				ins = ins + "null, "
			elif isinstance(each, int):
				ins = ins + str(each) + ", "
			else:
				ins = ins + "'" + str(each) + "', "
		ins = ins + "'" + str(log_in_status) + "')"
		#instruction to add to customer_phone
		phones = str(phone_number).split(',')
		new_ins_lst = []
		for i in range(len(phones)):
			new_ins = "INSERT INTO Customer_phone VALUES('" + email + "', " + phones[i] + ")"
			new_ins_lst.append(new_ins)
		cursor.execute(ins)
		for i in range(len(new_ins_lst)):
			cursor.execute(new_ins_lst[i])
		conn.commit()
		cursor.close()
		#set user log in status
		cursor = conn.cursor()
		query = "UPDATE Customer SET log_in_status='online' WHERE email='" + email + "';"
		print(query)
		cursor.execute(query)
		conn.commit()
		cursor.close()
		#add session
		session['customer'] = email
		return redirect(url_for('customer_home'))

#customer logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	email = session['customer']
	#set user log out status
	cursor = conn.cursor()
	query = "UPDATE Customer SET log_in_status='offline' WHERE email='" + email + "';"
	print(query)
	cursor.execute(query)
	conn.commit()
	cursor.close()
	#creates a session for the the user
	session.pop('customer')
	return redirect('/customer_login')


#staff login
@app.route('/staff_login')
def staff_login():
	return render_template('staff_login.html')
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	staff_password = request.form['staff_password']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Airline_staff WHERE username = %s and staff_password = %s'
	cursor.execute(query, (username, staff_password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the staff
		#session is a built in
		session['staff'] = username
		return redirect(url_for('staff_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid email or wrong password'
		return render_template('staff_login.html', error=error)


#staff register
@app.route('/staff_register')
def staff_register():
	return render_template('staff_register.html')
@app.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff():
	auth_codes = ['ABC123', 'DEF456']
	#grabs information from the forms
	# username 	staff_password 	first_name 	last_name 	date_of_birth 	airline_name 	emails	phones
	username = request.form['username']
	staff_password = request.form['staff_password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline_name = request.form['airline_name']
	auth_code = request.form['auth_code']
	emails = request.form['emails']
	phones = request.form['phones']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staff_register.html', error = error)
	elif (auth_code not in auth_codes):
		error = "Invalid authentication code"
		return render_template('staff_register.html', error = error)
	else:
		#executes query
		ins = "INSERT INTO Airline_staff VALUES("
		for each in [username, staff_password, first_name, last_name, date_of_birth]:
			ins = ins + "'" + each + "', "
		ins = ins + "'" + airline_name + "')"
		print('1 done')
		cursor.execute(ins)
		#instruction to add to staff_phone
		thephones = str(phones).split(',')
		new_ins_lst = []
		for i in range(len(thephones)):
			new_ins = "INSERT INTO Staff_phone VALUES('" + username + "', " + thephones[i] + ")"
			new_ins_lst.append(new_ins)
		for i in range(len(new_ins_lst)):
			cursor.execute(new_ins_lst[i])
		#instruction to add to staff_email
		theemails = str(emails).split(',')
		new_ins_lst = []
		for i in range(len(theemails)):
			new_ins = "INSERT INTO Staff_email VALUES('" + username + "', '" + theemails[i] + "')"
			new_ins_lst.append(new_ins)
		for i in range(len(new_ins_lst)):
			cursor.execute(new_ins_lst[i])
		conn.commit()
		cursor.close()
		session['staff'] = username
		return redirect(url_for('staff_home'))

#staff logout
@app.route('/logout_staff')
def logout_staff():
	session.pop('staff')
	return redirect('/staff_login')





#customer home
@app.route('/customer_home')
def customer_home():
	if ('customer' in session.keys()):
		email = session['customer']
		return render_template('customer_home.html', email=email)
	else:
		return redirect('/customer_login')

#view purchased flights
@app.route('/my_flights')
def my_flights():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	else:
		cursor = conn.cursor()
		option = 'future'
		query = "SELECT airline_name, flight_number, departure_date, departure_time FROM Purchase NATURAL JOIN Ticket where ((departure_date = NOW() and departure_time > NOW()) or (departure_date > NOW())) and email=%s"
		cursor.execute(query, (session['customer']))
		flights = cursor.fetchall()
		conn.commit()
		cursor.close()
		return render_template('my_flights.html', option=option, flights = flights)
@app.route('/my_flights/update', methods=['GET', 'POST'])
def update_my_flights():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	option = request.form['dropdown']
	if (option == 'future'):
		query = "SELECT airline_name, flight_number, departure_date, departure_time FROM Purchase NATURAL JOIN Ticket where ((departure_date = NOW() and departure_time > NOW()) or (departure_date > NOW())) and email=%s"
	elif (option == 'past'):
		query = "SELECT airline_name, flight_number, departure_date, departure_time FROM Purchase NATURAL JOIN Ticket where ((departure_date = NOW() and departure_time < NOW()) or (departure_date < NOW())) and email=%s"
	else:
		query = "SELECT airline_name, flight_number, departure_date, departure_time FROM Purchase NATURAL JOIN Ticket where email=%s"
	cursor.execute(query, (session['customer']))
	flights = cursor.fetchall()
	conn.commit()
	cursor.close()
	return render_template('my_flights.html', option=option, flights = flights)

#purchasing tickets
@app.route('/ticket_purchase', methods=['GET', 'POST'])
def ticket_purchase():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']
	depart_date = request.form['departure_date']
	depart_time = request.form['departure_time']
	query = "SELECT base_price, tickets_booked, seats from Flight NATURAL JOIN Airplane where airline_name=%s and flight_number=%s and departure_date=%s and departure_time=%s"
	cursor.execute(query, (airline_name, flight_number, depart_date, depart_time))
	results = cursor.fetchone()
	price = float(results['base_price'])
	tickets_booked = results['tickets_booked']
	total_seats = results['seats']
	if (tickets_booked/total_seats >= 0.8):
		price *= 1.25
	cursor.close()
	return render_template('ticket_purchase.html', airline_name=airline_name, flight_number=flight_number, departure_date=depart_date, departure_time=depart_time, price=price)
@app.route('/ticket_purchase/purchase', methods=['GET', 'POST'])
def purchase():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	expire_date = request.form['expiration_date']
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']
	depart_date = request.form['departure_date']
	depart_time = request.form['departure_time']
	query = "SELECT base_price, tickets_booked, seats from Flight NATURAL JOIN Airplane where airline_name=%s and flight_number=%s and departure_date=%s and departure_time=%s"
	cursor.execute(query, (airline_name, flight_number, depart_date, depart_time))
	results = cursor.fetchone()
	price = float(results['base_price'])
	tickets_booked = results['tickets_booked']
	total_seats = results['seats']
	if (tickets_booked/total_seats >= 0.8):
		price *= 1.25
	query = "SELECT max(id) FROM Ticket"
	cursor.execute(query)
	id = cursor.fetchone()['max(id)']
	id += 1
	email = session['customer']
	purchase_date = datetime.date.today()
	purchase_time = datetime.datetime.now().time()
	add_ticket = "insert into Ticket values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	cursor.execute(add_ticket, (id, first_name, last_name, date_of_birth, price, card_type, card_number, name_on_card, expire_date, purchase_date, purchase_time, flight_number, depart_date, depart_time, airline_name))
	conn.commit()
	add_to_purchase = "insert into Purchase values (%s, %s, null, null);"
	cursor.execute(add_to_purchase, (email, id))
	conn.commit()
	tickets_booked += 1
	query = "UPDATE Flight SET tickets_booked=%s"
	cursor.execute(query, tickets_booked)
	conn.commit()
	cursor.close()
	return render_template('flight_search.html', loggedin=True)

#cancel flight ticket
@app.route('/cancel_trip', methods=['GET', 'POST'])
def cancel_trip():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	query = "SELECT id, airline_name, flight_number, departure_date, departure_time FROM Purchase NATURAL JOIN Ticket where timestamp(concat(departure_date, ' ', departure_time)) > (NOW() + INTERVAL 24 HOUR) and email=%s"
	email = session['customer']
	cursor.execute(query, (email))
	tickets = cursor.fetchall()
	cursor.close()
	return render_template('cancel_trip.html', tickets=tickets)
@app.route('/cancel_trip/cancel', methods=['GET', 'POST'])
def cancel():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	email = session['customer']
	ticket_id = request.form['ticket_id']
	delete_purchase = "DELETE FROM Purchase where email=%s and id=%s"
	cursor.execute(delete_purchase, (email, ticket_id))
	conn.commit()
	delete_ticket = "DELETE FROM Ticket where id=%s"
	cursor.execute(delete_ticket, ticket_id)
	conn.commit()
	cursor.close()
	print("canceled trip")
	return redirect('/customer_home')


#rate and comment
@app.route('/rate_and_comment', methods=['GET', 'POST'])
def rate_and_comment():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	email = session['customer']
	query = "SELECT T.id, F.airline_name, F.flight_number, F.departure_date, F.departure_time, rate, comments FROM Purchase NATURAL JOIN Ticket as T INNER JOIN Flight as F where (T.airline_name=F.airline_name and T.flight_number=F.flight_number and T.departure_date=F.departure_date and T.departure_time=F.departure_time) and timestamp(concat(arrival_date, ' ', arrival_time)) < NOW() and email=%s"
	cursor.execute(query, email)
	flights = cursor.fetchall()
	cursor.close()
	return render_template('rate_and_comment.html', flights=flights)
@app.route('/rate_and_comment/posting_page', methods=['GET', 'POST'])
def posting_page():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	ticket_id = request.form['ticket_id']
	return render_template('rate_comment_post.html', ticket_id=ticket_id)
@app.route('/rate_and_comment/posting_page/post', methods=['GET', 'POST'])
def post():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	email = session['customer']
	ticket_id = request.form['ticket_id']
	rating = request.form['rating']
	comment = request.form['comment']
	post_comment = "UPDATE Purchase SET rate=%s, comments=%s where id=%s and email=%s"
	cursor.execute(post_comment, (rating, comment, ticket_id, email))
	conn.commit()
	cursor.close()
	return redirect(url_for('rate_and_comment'))


#track spending
@app.route('/spending')
def spending():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	email = session['customer']
	query = "SELECT MONTHNAME(purchase_date) as month, sum(price) as spending FROM Purchase NATURAL JOIN Ticket where purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) and email=%s GROUP BY MONTH(purchase_date) ORDER by MONTH(purchase_date) ASC;"
	cursor.execute(query, email)
	results = cursor.fetchall()
	total = 0
	for line in results:
		total += line['spending']
	return render_template('spending.html', results=results, total=total)
@app.route('/spending/ranged', methods=['GET', 'POST'])
def rangedspending():
	if ('customer' not in session.keys()):
		return redirect('/customer_login')
	cursor = conn.cursor()
	email = session['customer']
	start = request.form['start_date']
	end = request.form['end_date']
	query = "SELECT MONTHNAME(purchase_date) as month, sum(price) as spending FROM Purchase NATURAL JOIN Ticket where purchase_date >= %s and purchase_date <= %s and email=%s GROUP BY MONTH(purchase_date) ORDER by MONTH(purchase_date) ASC;"
	cursor.execute(query, (start, end, email))
	results = cursor.fetchall()
	total = 0
	for line in results:
		total += line['spending']
	return render_template('spending.html', results=results, total=total)



#staff_home
@app.route('/staff_home')
def staff_home():
	if ('staff' in session.keys()):
		username = session['staff']
		return render_template('staff_home.html', username=username)
	else:
		return redirect('/staff_login')

@app.route('/view_flights_staff')
def view_flights_staff():
	if ('staff' in session.keys()):
		#get airline name
		username = session['staff']
		cursor = conn.cursor()
		query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
		cursor.execute(query, (username))
		airline_name = cursor.fetchall()[0]['airline_name']
		conn.commit()
		cursor.close()
		#get flights
		cursor = conn.cursor()
		query = "SELECT * FROM Flight WHERE airline_name=%s and (departure_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY))"
		cursor.execute(query, (airline_name))
		flights = cursor.fetchall()
		conn.commit()
		cursor.close()
		#print(flights)
		return render_template('view_flights_staff.html', flights=flights)
	else:
		return redirect('/staff_login')

#add airplane
@app.route('/add_airplane')
def add_airplane():
	if ('staff' in session.keys()):
		return render_template('add_airplane.html')
	else:
		return redirect('/staff_login')
@app.route('/add_airplaneAuth', methods=['GET', 'POST'])
def add_airplaneAuth():
	#data from form
	id = request.form['id']
	seats = request.form['seats']
	manufacturer = request.form['manufacturer']
	manufacturing_date = request.form['manufacturing_date']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']
	conn.commit()
	cursor.close()
	#check if airplane already exists
	cursor = conn.cursor()
	query = "SELECT * FROM Airplane WHERE id = %s"
	cursor.execute(query, (id))
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		error = "This airplane already exists"
		return render_template('add_airplane.html', error = error)
	else:
		#add airplane
		ins = "INSERT INTO Airplane VALUES(%s, %s, %s, %s, null, %s)"
		cursor.execute(ins, (id, seats, manufacturer, manufacturing_date, airline_name))
		conn.commit()
		cursor.close()
		return view_airplanes()
@app.route('/view_airplanes')
def view_airplanes():
	if ('staff' in session.keys()):
		username = session['staff']
		#print(username)
		cursor = conn.cursor()
		query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
		cursor.execute(query, (username))		
		airline_name = cursor.fetchall()[0]['airline_name']
		#print(airline_name)
		conn.commit()
		cursor.close()
		cursor = conn.cursor()
		query = "SELECT id FROM Airplane WHERE airline_name='" + airline_name + "'"
		cursor.execute(query)
		airplanes = cursor.fetchall()
		#print(airplanes)
		conn.commit()
		cursor.close()
		return render_template('view_airplanes.html', airplanes=airplanes)
	else:
		return redirect('/staff_login')

#add airport
@app.route('/add_airport')
def add_airport():
	if ('staff' in session.keys()):
		return render_template('add_airport.html')
	else:
		return redirect('/staff_login')
@app.route('/add_airportAuth', methods=['GET', 'POST'])
def add_airportAuth():
	#data from form
	airport_code = request.form['airport_code']
	name = request.form['name']
	city = request.form['city']
	country = request.form['country']
	type = request.form['type']
	#check if airport already exists
	cursor = conn.cursor()
	query = "SELECT * FROM Airport WHERE airport_code = %s"
	cursor.execute(query, (airport_code))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "This airport already exists"
		return render_template('add_airport.html', error = error)
	else:
		#add airport
		ins = "INSERT INTO Airport VALUES(%s, %s, %s, %s, %s)"
		cursor.execute(ins, (airport_code, name, city, country, type))
		conn.commit()
		cursor.close()
		return view_airports()
@app.route('/view_airports')
def view_airports():
	if ('staff' in session.keys()):
		cursor = conn.cursor()
		query = "SELECT * FROM Airport"
		cursor.execute(query)
		airports = cursor.fetchall()
		conn.commit()
		cursor.close()
		return render_template('view_airports.html', airports=airports)
	else:
		return redirect('/staff_login')

#create new flight
@app.route('/create_new_flights')
def create_new_flights():
	if ('staff' in session.keys()):
		return render_template('create_new_flights.html')
	else:
		return redirect('/staff_login')
@app.route('/create_new_flightsAuth', methods=['GET', 'POST'])
def create_new_flightsAuth():
	#data from form
	flight_number = request.form['flight_number']
	base_price = request.form['base_price']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	arrival_date = request.form['arrival_date']
	arrival_time = request.form['arrival_time']
	flight_status = 'on time'
	tickets_booked = 0
	id = request.form['id']
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']
	#check if flight already exists
	cursor = conn.cursor()
	query = "SELECT * FROM Flight WHERE flight_number = %s and departure_date = %s and departure_time = %s and airline_name = %s"
	cursor.execute(query, (flight_number, departure_date, departure_time, airline_name))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "This flight already exists"
		return render_template('create_new_flights.html', error = error)
	else:
		#add airport
		ins = "INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(ins, (flight_number, base_price, departure_date, departure_time, arrival_date, arrival_time, flight_status, tickets_booked, id, airline_name, departure_airport, arrival_airport))
		conn.commit()
		cursor.close()
		return view_flights_staff()

#change flight status
@app.route('/change_flight_status')
def change_flight_status():
	if ('staff' in session.keys()):
		return render_template('change_flight_status.html')
	else:
		return redirect('/staff_login')
@app.route('/change_flight_statusAuth', methods=['GET', 'POST'])
def change_flight_statusAuth():
	#data from form
	flight_number = request.form['flight_number']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	flight_status = request.form['flight_status']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']
	#change
	ins = "UPDATE Flight SET flight_status=%s WHERE flight_number=%s and departure_date=%s and departure_time=%s and airline_name=%s"
	cursor.execute(ins, (flight_status, flight_number, departure_date, departure_time, airline_name))
	conn.commit()
	cursor.close()
	return view_flights_staff()

#view customers in flight
@app.route('/customer_in_flight')
def customer_in_flight():
	if ('staff' in session.keys()):
		return render_template('customer_in_flight.html')
	else:
		return redirect('/staff_login')
@app.route('/customer_in_flightAuth', methods=['GET', 'POST'])
def customer_in_flightAuth():
	#data from form
	flight_number = request.form['flight_number']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']	
	conn.commit()
	cursor.close()
	#find customer
	cursor = conn.cursor()
	ins = "SELECT first_name, last_name FROM Ticket WHERE flight_number=%s and departure_date=%s and departure_time=%s and airline_name=%s"
	cursor.execute(ins, (flight_number, departure_date, departure_time, airline_name))
	customers = cursor.fetchall()
	conn.commit()
	cursor.close()
	return render_template('customer_in_flight.html', customers=customers)

#view ratings
@app.route('/view_ratings')
def view_ratings():
	if ('staff' in session.keys()):
		cursor = conn.cursor()
		#get airline name
		username = session['staff']
		cursor = conn.cursor()
		query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
		cursor.execute(query, (username))
		airline_name = cursor.fetchall()[0]['airline_name']
		conn.commit()
		cursor.close()
		#find ratings
		cursor = conn.cursor()
		query = "SELECT AVG(rate), flight_number FROM Purchase natural join Ticket where airline_name=%s GROUP BY flight_number"
		cursor.execute(query, (airline_name))
		ratings = cursor.fetchall()
		conn.commit()
		cursor.close()
		return render_template('view_ratings.html', ratings=ratings)
	else:
		return redirect('/staff_login')

#view frequent customers
@app.route('/view_frequent_customer')
def view_frequent_customer():
	if ('staff' in session.keys()):
		cursor = conn.cursor()
		#get airline name
		username = session['staff']
		cursor = conn.cursor()
		query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
		cursor.execute(query, (username))
		airline_name = cursor.fetchall()[0]['airline_name']
		conn.commit()
		cursor.close()
		#find all ratings
		cursor = conn.cursor()
		query = "SELECT email, COUNT(*) as count FROM Purchase natural join Ticket where airline_name=%s GROUP BY email ORDER BY count DESC; "
		cursor.execute(query, (airline_name))
		customer = cursor.fetchall()
		conn.commit()
		cursor.close()
		#find ratings in last one year
		cursor = conn.cursor()
		query = "SELECT email, COUNT(*) as count FROM Purchase NATURAL JOIN Ticket WHERE airline_name = %s AND departure_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -365 DAY) AND CURDATE() GROUP BY email ORDER BY count DESC; "
		cursor.execute(query, (airline_name))
		customer1 = cursor.fetchall()
		conn.commit()
		cursor.close()
		return render_template('view_frequent_customer.html', customer=customer, customer1=customer1)
	else:
		return redirect('/staff_login')

#view report
@app.route('/view_reports')
def view_reports():
	if ('staff' in session.keys()):
		return render_template('view_reports.html')
	else:
		return redirect('/staff_login')
@app.route('/view_reportsAuth', methods=['GET', 'POST'])
def view_reportsAuth():
	#data from form
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']	
	conn.commit()
	cursor.close()
	#find report
	cursor = conn.cursor()
	ins = "SELECT COUNT(*) as count FROM Ticket WHERE airline_name=%s and (purchase_date BETWEEN %s AND %s); "
	cursor.execute(ins, (airline_name, start_date, end_date))
	result = cursor.fetchall()[0]['count']
	conn.commit()
	cursor.close()
	return render_template('view_reports.html', result=result)

#view earned revenue
@app.route('/view_earned_revenue')
def view_earned_revenue():
	if ('staff' in session.keys()):
		cursor = conn.cursor()
		#get airline name
		username = session['staff']
		cursor = conn.cursor()
		query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
		cursor.execute(query, (username))
		airline_name = cursor.fetchall()[0]['airline_name']
		conn.commit()
		cursor.close()
		#find total revenue
		cursor = conn.cursor()
		query = "SELECT SUM(price) as total FROM Purchase NATURAL JOIN Ticket WHERE airline_name = %s; "
		cursor.execute(query, (airline_name))
		revenue = cursor.fetchall()[0]['total']
		conn.commit()
		cursor.close()
		#find total revenue in last one month
		cursor = conn.cursor()
		query = "SELECT SUM(price) as total FROM Purchase NATURAL JOIN Ticket WHERE airline_name = %s AND departure_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -30 DAY) AND CURDATE(); "
		cursor.execute(query, (airline_name))
		revenue_month = cursor.fetchall()[0]['total']
		conn.commit()
		cursor.close()
		#find total revenue in last one year
		cursor = conn.cursor()
		query = "SELECT SUM(price) as total FROM Purchase NATURAL JOIN Ticket WHERE airline_name = %s AND departure_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -365 DAY) AND CURDATE(); "
		cursor.execute(query, (airline_name))
		revenue_year = cursor.fetchall()[0]['total']
		conn.commit()
		cursor.close()
		return render_template('view_earned_revenue.html', revenue=revenue, revenue_month=revenue_month, revenue_year=revenue_year)
	else:
		return redirect('/staff_login')

#search flight
@app.route('/staff_search_flight')
def staff_search_flight():
	if ('staff' in session.keys()):
		return render_template('staff_search_flight.html')
	else:
		return redirect('/staff_login')
@app.route('/staff_search_flightAuth', methods=['GET', 'POST'])
def staff_search_flightAuth():
	#data from form
	search_type = request.form['search_type']
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']
	#get airline name
	username = session['staff']
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM Airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchall()[0]['airline_name']	
	conn.commit()
	cursor.close()
	#find flight
	cursor = conn.cursor()
	if (search_type == 'time_period'):
		ins = "SELECT * from Flight WHERE airline_name=%s and (departure_date BETWEEN %s AND %s); "
		cursor.execute(ins, (airline_name, start_date, end_date))
		result = cursor.fetchall()
	elif (search_type == 'airport_code'):
		ins = "SELECT * from Flight WHERE airline_name=%s and departure_airport=%s and arrival_airport=%s;"
		cursor.execute(ins, (airline_name, departure_airport, arrival_airport))
		result = cursor.fetchall()
	else: #both
		ins = "SELECT * from Flight WHERE airline_name=%s and departure_airport=%s and arrival_airport=%s and (departure_date BETWEEN %s AND %s); "
		cursor.execute(ins, (airline_name, departure_airport, arrival_airport, start_date, end_date))
		result = cursor.fetchall()
	conn.commit()
	cursor.close()
	return render_template('staff_search_flight.html', result=result)


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)