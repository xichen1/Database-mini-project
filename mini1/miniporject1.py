import sqlite3
import re 
import time, datetime
from datetime import  date
from getpass import getpass 
connection = None
cursor = None
def main():
	global connection, cursor
	dbname = input("Enter a name of the datatase, if there is no such datatase, the program will create one automatically: ")
	connection = sqlite3.connect("./"+dbname)
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(' PRAGMA foreign_keys=ON; ')
	Login()
	connection.close()

def Login():
	global connection, cursor 
	# Login 
	correct = 0
	while correct == 0:
		username = input("Enter username:").lower()
		password = getpass()       # getpass function does not reveal the password as it is typed and stores the password in the variable 
		
		if re.match("^[A-Za-z0-9_]*$", username) and re.match("^[A-Za-z0-9_]*$", password):  # Condition to make sure username & password contains only letters and numbers.
			cursor.execute('SELECT * FROM users WHERE LOWER(uid)=? and pwd=?;' , (username, password))
			user= cursor.fetchone()
			if user != None:
				user_fname = user['fname']
				user_lname = user['lname']
				user_city = user['city']
				
				print("Login successful!")
				print("Hi", user_fname, user_lname)
				out = Menu(user['utype'], user['uid'])
				if out == 0:
					print("Logout!")
					continue
				elif out == 1:
					print("Quitting program!")
					return
						  
			else:
				print("Invalid username/password!")
				continue
					 
		else:
			print("Username/password should only contain numbers and letters")
			continue

def Menu(utype, uid):
	print("Enter 'Logout' to logout")
	print("Enter a blank line to exit")
	while True:
		# Displaying menu based on the current user. 
		if utype == "a":
			print('''Current user is a registry agent. You may
			1. Register a birth
			2. Register a marriage
			3. Renew a vehicle registration 
			4. Process a bill of sale 
			5. Process a payment 
			6. Get a driver abstract''')
			
			command = input("Please enter your command: ")
			if command == "":
				return 1
			if command.lower() == "logout":
				print("Logout successful!")
				return 0            
			
			if command in ["Register a birth", "1"]:
				registerBirth(uid)
			elif command in ["Register a marriage", "2"]:
				marriage_reg(uid)
			elif command in ["Renew a vehicle registration", "3"]:
				renew_a_vehicle_registration()
			elif command in ["Process a bill of sale", "4"]:
				salebill()
			elif command in ["Process a payment", "5"]:
				processPayment()
			elif command in ["Get a driver abstract", "6"]:
				getabst()
			else:
				print("Invalid command. Please enter again.")
					   
		else:
			print(''' Current user is an officer. You may 
			1. Issue a ticket
			2. Find a car owner''')
			
			command = input("Please enter your command: ")
			
			if command == "":
				return 1
			if command.lower() == "logout":
				print("Logout successful!")
				return 0         
				
			if command in ["Issue a ticket", "1"]:
				issue_a_ticket()
			elif command in ['Find a car owner', "2"]:
				find_a_car_owner() 
		connection.commit()

def registerBirth(username):
	global connection, cursor
	
	# User input
	# while loop is to ensure user input is valid. 
	while True:
		fname = input("Enter newborn's first name: ").lower()
		lname = input("Enter newborn's last name: ").lower()
		gender = input("Enter newborn's gender: ")
		bdate = input("Enter newborn's birthdate (YYYY-MM-DD): ")
		bplace = input("Enter newborn's birthplace: ")
		f_fname = input("Enter father's first name: ").lower()
		f_lname = input("Enter father's last name: ").lower()
		m_fname = input("Enter mother's first name: ").lower()
		m_lname = input("Enter mother's last name: ").lower()
		username = username.lower()
		# Converting bdate to str
		try:
			temp = datetime.datetime.strptime(bdate, "%Y-%m-%d")
		except:
			print("Wrong birthdate format. Enter again.")
			continue
		bdate = temp.date()
		
		names = [fname, lname, f_fname, f_lname, m_fname, m_lname]
		namecheck = 1
		for each in names:
			if not re.match("^[-A-Za-z0-9_]*$", each):
				print("You can only use letters and numbers for the names")
				namecheck = 0
				break;
		if namecheck==0:
			continue
		cursor.execute("SELECT city FROM users WHERE lower(uid) = ?;", (username,)) # Query to obtain the user's city
		regplace = cursor.fetchone()[0]

		
		regdate = date.today()
		
		cursor.execute("SELECT MAX(regno) FROM births;") # Query to obtain a unique number. 
		regno = cursor.fetchone()[0]
		
		if regno == None:
			regno = 1
		else:
			regno += 1
		
		#Checking input
		fields = [regno, fname, lname, regplace, gender, bdate, bplace, f_fname, f_lname, m_fname, m_lname]
		blankcheck = 0
		for each in fields:
			if each == "":          # Prevents blanks
				print("No blanks allowed. All fields are mandatory")
				blankcheck = 1
				break;
		if blankcheck == 1:
			continue
		   
			  
		if fname != "" and (f_fname == m_fname or fname == f_fname or fname == m_fname or f_fname == m_fname):
				print("Two persons of the same family can't have the same first name")
			
		else: 
			break 
		
		
	# Condition to make sure birth has not already been registered 
	cursor.execute("SELECT NOT EXISTS (SELECT * FROM births WHERE LOWER(fname) = ? AND LOWER(lname) = ?);", (fname, lname))
	BirthNotExists = cursor.fetchone()[0]
	
	# Checking if the parents exist in the database
	# If the father does not exist, take user input and insert into table persons
	cursor.execute("SELECT EXISTS(SELECT * FROM persons WHERE LOWER(fname) = ? AND LOWER(lname) = ?);", (f_fname, f_lname)) 
	fatherExists = cursor.fetchone()
	
	
	if fatherExists == False:
		f_bdate = input("Enter the father's birthdate: ")
		f_bplace = input("Enter the father's birthplace: ")
		f_address = input("Enter the father's address: ")
		f_phone = input("Enter the father's phone: ")
		
		cursor.execute("INSERT INTO persons VALUES(?, ?, ?, ?, ?, ?)", (f_fname, f_lname, f_bdate, f_bplace, f_address, f_phone))
		connection.commit()
	else:
		cursor.execute("SELECT fname, lname FROM persons WHERE LOWER(fname) = ? AND LOWER(lname) = ?;", (f_fname, f_lname))
		f = cursor.fetchone()
		f_fname = f[0]
		f_lname = f[1]

	# If the mother does not exist, take user input and insert into table persons 
	cursor.execute("SELECT EXISTS(SELECT * FROM persons WHERE LOWER(fname) = ? AND LOWER(lname) = ?);", (m_fname, m_lname)) 
	motherExists = cursor.fetchone()


	
	if motherExists == False:
		m_bdate = input("Enter the mother's birthdate: ")
		m_bplace = input("Enter the mother's birthplace: ")
		m_address = input("Enter the mother's address: ")
		m_phone = input("Enter the mother's phone: ")
		
		cursor.execute("INSERT INTO persons VALUES(?, ?, ?, ?, ?, ?)", (m_fname, m_lname, m_bdate, m_bplace, m_address, m_phone))
		connection.commit()
	else:
		cursor.execute("SELECT fname, lname FROM persons WHERE LOWER(fname) = ? AND LOWER(lname) = ?;", (m_fname, m_lname))
		m = cursor.fetchone()
		m_fname = m[0]
		m_lname = m[1]
		
	# Searching for the mother's phone number and address
	mf = m_fname.lower()
	ml = m_lname.lower()
	cursor.execute("SELECT address, phone FROM persons WHERE lower(fname) = ? and lower(lname) = ?;", (mf, ml))
	information = cursor.fetchone()
	m_phone = information['phone']
	m_address = information['address']
	
	# Searching the datebase in case two people have the same name
	cursor.execute("SELECT fname, lname FROM persons WHERE lower(fname) = ? and lower(lname) = ?;", (fname,lname))
	personexist = cursor.fetchall()
	if personexist != []:
		print("Invalid name, name has already taken by others. Returning to menu.")
		return
	# If birth does not exist, then insert 
	if BirthNotExists:
		cursor.execute("INSERT INTO persons VALUES(?, ?, ?, ?, ?, ?);", (fname, lname, bdate, bplace, m_address, m_phone))        
		cursor.execute("INSERT INTO births VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname))
		print("Birth registered successfully")
		
	else:
		print("Birth already registered")
		
	connection.commit()


def marriage_reg(username):
	global connection, cursor

	uid = username 
	p1_f = p1_l = p2_f = p2_l = ""
	while True:
		p1_f = input("Enter the first person's first name: ")
		p1_l = input("Enter the first person's last name: ")
		p2_f = input("Enter the second person's first name: ")
		p2_l = input("Enter the second person's last name: ")
		if p1_f != "" and p1_l != "" and p2_f != "" and p2_l != "":
			break;
		elif p1_l == p2_l and p1_f == p2_f:
			print("You cannot enter two same names, please enter again.\n") # two same people cannot marry
		else:
			print("You cannot enter empty name(s), please enter again.\n") # cannot enter empty name
	p1fl = p1_f.lower()
	p1ll = p1_l.lower()
	p2fl = p2_f.lower()
	p2ll = p2_l.lower()
	cursor.execute("select * from persons where lower(fname)=:f and lower(lname)=:l;", {"f":p1fl, "l":p1ll})
	p1exist = cursor.fetchall()
	# finding if the first person's name is in persons table
	if  p1exist == []:
		p1_bdate = input("Enter the first person's birth date: ")
		p1_bplace = input("Enter the first person's birth place: ")
		p1_address = input("Enter the first person's address: ")
		p1_phone = input("Enter the first person's phone number: ")
		if p1_bdate == "":
			p1_bdate = None
		if p1_bplace == "":
			p1_bplace = None
		if p1_address == "":
			p1_address = None
		if p1_phone == "":
			p1_phone = None
		insertp1 = '''
				insert into persons(fname, lname, bdate, bplace, address, phone) values
				(:fn, :ln, :bd, :bp, :ad, :ph);
		'''
		cursor.execute(insertp1, {"fn":p1_f, "ln": p1_l, "bd": p1_bdate, "bp": p1_bplace, "ad": p1_address, "ph":p1_phone})

	cursor.execute("select * from persons where lower(fname)=? and lower(lname)=?;", (p2fl, p2ll))
	p2exist = cursor.fetchall()	
	# finding if the second person's name is in persons table
	if p2exist == []:
		p2_bdate = input("Enter the second person's birth date: ")
		p2_bplace = input("Enter the second person's birth place: ")
		p2_address = input("Enter the second person's address: ")
		p2_phone = input("Enter the second person's phone number: ")
		if p2_bdate == "":
			p2_bdate = None
		if p2_bplace == "":
			p2_bplace = None
		if p2_address == "":
			p2_address = None
		if p2_phone == "":
			p2_phone = None
		insertp2 = '''
				insert into persons(fname, lname, bdate, bplace, address, phone) values
				(:fn, :ln, :bd, :bp, :ad, :ph);
		'''
		cursor.execute(insertp2, {"fn":p2_f, "ln": p2_l, "bd": p2_bdate, "bp": p2_bplace, "ad": p2_address, "ph":p2_phone})
	# get the original names from persons table (no lowercase or upper case)
	cursor.execute("select fname, lname from persons where lower(fname)=? and lower(lname)=?;", (p1fl, p1ll))
	p1 = cursor.fetchone()
	f1 = p1[0]
	l1 = p1[1]
	cursor.execute("select fname, lname from persons where lower(fname)=? and lower(lname)=?;", (p2fl, p2ll))
	p2 = cursor.fetchone()	
	f2 = p2[0]
	l2 = p2[1]
	current_date = time.strftime("%Y-%m-%d")
	findlocation = '''
				select city
				from users
				where uid=:u;
				'''
	# assign a number by finding the largest number
	findnownum = '''
				select MAX(regno)
				from marriages;
	'''
	cursor.execute(findlocation, {"u":uid})
	loc = (cursor.fetchone())[0]
	cursor.execute(findnownum) 
	num = (cursor.fetchone())[0]
	if num == None:
		num = 1
	else:
		num += 1
	insertval = '''
				insert into marriages(regno, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname) values
				(:n, :d, :p, :p1f, :p1l, :p2f, :p2l);
	'''
	cursor.execute(insertval, {"n": num, "d":current_date, "p":loc, "p1f":f1, "p1l":l1, "p2f":f2, "p2l":l2})
	print("Register successfully, returning to menu.")
	connection.commit()
	return


def renew_a_vehicle_registration():
	# ask the user for the input
	while True:
		regno = input("Enter registration number:")
		if regno.isdigit() is False:
			print("The input type is wrong")
			continue
		cursor.execute('''
		SELECT expiry
		FROM registrations
		WHERE regno = ?;''', (regno,))
		expiry_date1 = cursor.fetchall()
		if expiry_date1 == []:
			print("The regno does not exist, enter again.")
			continue
		else:
			break
	# 	check the registration number is exists or not


	new_expiry1 = incrementYear(expiry_date1[0][0])
	current_date = time.strftime("%Y-%m-%d")
	# call the function to generate the new expiry date
	if expiry_date1[0][0] <= current_date[0]:

		new_expiry2 = incrementYear(current_date)
		# set the 1 year after the current date for the new expiry date
		print("new expiry date: " + new_expiry2)
		cursor.execute('''
				UPDATE registrations
				SET expiry = ?
				WHERE regno = ?;''', (new_expiry2, regno))
	else:
		print("new expiry date: " + new_expiry1)
		cursor.execute('''
				UPDATE registrations
				SET expiry = ?
				WHERE regno = ?;''', (new_expiry1, regno))
		# update the new expiry date to the database


def salebill():
	global connection, cursor
	vin = c_fname = c_lname = n_fname = n_lname = ""
	print("Enter the details.")
	while True:
		vin = input("Enter the vin of car: ")
		c_fname = input("Enter the current owner's first name: ")
		c_lname = input("Enter the current owner's last name: ")
		n_fname = input("Enter the new owner's first name: ")
		n_lname = input("Enter the new owner's last name: ")
		plate = input("Enter the plate number: ")
		if vin != "" and c_fname != "" and c_lname != "" and n_fname != "" and n_lname != "" and plate != "":
			break
		elif c_fname == n_fname and c_lname == n_lname:
			print("You cannot transfer the car from one person to the same person.\nTry again.")
		else:
			print("You cannot enter any empty information.\nTry again.")
	cfl = c_fname.lower()
	cll = c_lname.lower()
	nfl = n_fname.lower()
	nll = n_lname.lower()
	# to find if the person is in the persons table or not
	cursor.execute("select fname, lname from persons where lower(fname)=? and lower(lname)=?;",(cfl, cll))
	c = cursor.fetchall()
	cursor.execute("select fname, lname from persons where lower(fname)=? and lower(lname)=?;",(nfl, nll))
	n = cursor.fetchall()

	if c==[] or n==[]:
		print("The person's detail is not in the database.\nReturn to main menu.")
		return


	tofindreg = '''
			select regno, fname, lname, r.vin
			from registrations r, vehicles v
			where r.vin = v.vin
			and lower(r.vin) = :vi
			ORDER BY r.regdate ASC;
	'''
	cursor.execute(tofindreg, {"vi": vin.lower()})
	# to find if the vin is in the registrations table or not
	reg = cursor.fetchall()
	if reg == []:
		print("Invalid vin, return to main menu.")
		return
	if (reg[0][1]).lower() != cfl or (reg[0][2]).lower() != cll: 
		print("Wrong current owner's name, return to main menu.")
		return
	old_regno = reg[0][0]
	vi = reg[0][3]
	current_date = time.strftime("%Y-%m-%d")
	oneyear_later = (datetime.datetime.now() + datetime.timedelta(days = 365)).strftime("%Y-%m-%d")
	findnownum = '''
				select MAX(regno)
				from registrations;
	'''
	cursor.execute(findnownum) 
	new_regno = (cursor.fetchone())[0]
	if new_regno == None:
		new_regno = 1
	else:
		new_regno += 1
	changeold = '''
			update registrations
			set expiry = :cdate
			where regno = :reg;
	'''
	insertnew = '''
			insert into registrations(regno, regdate, expiry, plate, vin, fname, lname) values
			(:nreg, :regd, :expd, :pla, :vi, :fn, :ln);

	'''
	# update the old registration
	cursor.execute(changeold, {"cdate": current_date, "reg": old_regno})
	# insert the new registration
	cursor.execute(insertnew, {"nreg": new_regno, "regd": current_date, "expd": oneyear_later, "pla": plate, "vi": vi, "fn": n_fname, "ln": n_lname})
	print("The bill is processed successfully.")
	return


def processPayment():
	global connection, cursor
	# Input values
	tno = input("Please enter the ticket number:")
	amount = input("Please enter the payment amount:")
	current_date = time.strftime("%Y-%m-%d")
	if not tno.isdigit():
		print("Ticket number must be a number, returning to menu.")
		return
	if not amount.isdigit():
		print("Amount must be a number, returning to menu.")
		return

	# Checking if ticket number exists
	cursor.execute('SELECT EXISTS( SELECT * FROM tickets WHERE tno = :num);', {"num":tno})
	valid_ticket = cursor.fetchone()[0]
	
	cursor.execute('''select * from payments where tno=:tn;''', {"tn":tno})
	inpayment = cursor.fetchall()
	# Checking if amount does not exceed
	# Query will return True if there is the ticket number whose payments do not exceed the fine
	if inpayment != []:
		cursor.execute('''SELECT EXISTS(
		SELECT payments.tno    
		FROM payments
		LEFT JOIN tickets
		ON payments.tno = tickets.tno
		GROUP BY payments.tno 
		HAVING (SUM(amount) + ? ) <= fine 
		AND tickets.tno = ?);''', (amount, tno))
		validPayment = cursor.fetchone()[0]
	else:
		cursor.execute('''SELECT EXISTS(
		SELECT payments.tno    
		FROM payments
		LEFT JOIN tickets
		ON payments.tno = tickets.tno
		GROUP BY payments.tno 
		HAVING ? <= fine 
		AND tickets.tno = ?);''', (amount, tno))
		validPayment = cursor.fetchone()[0]		

	
	cursor.execute('''SELECT NOT EXISTS(
	SELECT *
	FROM payments
	WHERE tno = ? AND pdate = ?);''', (tno, current_date))
	onePayment = cursor.fetchone()[0]
	
	if valid_ticket and validPayment and onePayment:
		cursor.execute('INSERT INTO payments VALUES (?, ?, ?);', (tno, current_date, amount))
		print("Payment processed successfully")
	
	elif not valid_ticket:
		print("This person does not have a ticket")
	
	elif not validPayment:
		print("Sum of payments cannot exceed fine amount!")
		
	elif not onePayment:
		print("This person can only pay once a day")
	
	connection.commit()	
	return


def getabst():
	global connection, cursor
	f_name = l_name = ""
	while True:
		f_name = input("Enter the first name: ")
		l_name = input("Enter the last name: ")
		if f_name != "" and l_name != "":
			break
		else:
			print("invalid")
	f_name = f_name.lower()
	l_name = l_name.lower()
	findperson ='''
	select fname, lname
	from registrations
	where lower(fname) = :f and lower(lname)= :l
	'''
	cursor.execute(findperson, {"f":f_name, "l":l_name})
	person = cursor.fetchall()
	if person == []:
		print("The name you enter does not have any vehicles and registrations.")
		return
	# last two years
	findticket2 = '''
		select fname, lname, count(tno) from
		tickets t
		left join registrations r
		on r.regno = t.regno
		where t.vdate > DateTime('Now', 'LocalTime', '-2 Years')
		group by r.fname, r.lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(findticket2, {"f":f_name, "l":l_name})
	ticket2 = cursor.fetchone()
	finddemerit2 = '''
		select ddate, fname, lname, count(*)
		from demeritNotices
		where ddate > DateTime('Now', 'LocalTime', '-2 Years')
		group by fname, lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(finddemerit2, {"f":f_name, "l":l_name})
	demerit2 = cursor.fetchone()
	findpoint2 = '''
		select fname, lname, sum(points)
		from demeritNotices
		where ddate > DateTime('Now', 'LocalTime', '-2 Years')
		group by fname, lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(findpoint2, {"f":f_name, "l":l_name})
	point2 = cursor.fetchone()
	print("For the past two years: ")
	if ticket2 is None:
		print("ticket number is 0.")
	else:
		print("ticket number is: "+ str(ticket2[2])+".")
	if demerit2 is None:
		print("Number of demeritNotices is 0.")
	else:
		print("Number of demeritNotices is: "+ str(demerit2[3])+".")
	if point2 is None:
		print("Total number of demerit points is: 0.")
	else:
		print("Total number of demerit points is: " + str(point2[2])+".")

	# lifetime
	findticketl = '''
		select fname, lname, count(tno) from
		tickets t
		left join registrations r
		on r.regno = t.regno
		group by r.fname, r.lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(findticketl, {"f":f_name, "l":l_name})
	ticketl = cursor.fetchone()
	finddemeritl = '''
		select ddate, fname, lname, count(*)
		from demeritNotices
		group by fname, lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(finddemeritl, {"f":f_name, "l":l_name})
	demeritl = cursor.fetchone()
	findpointl = '''
		select fname, lname, sum(points)
		from demeritNotices
		group by fname, lname
		having lower(fname) = :f and lower(lname) = :l;
	'''
	cursor.execute(findpointl, {"f":f_name, "l":l_name})
	pointl = cursor.fetchone()
	print("\nFor the lifetime:")
	if ticketl is None:
		print("ticket number is 0.")
	else:
		print("ticket number is: "+ str(ticketl[2])+".")
	if demeritl is None:
		print("Number of demeritNotices is 0.")
	else:
		print("Number of demeritNotices is: "+ str(demeritl[3])+".")
	if pointl is None:
		print("Total number of demerit points is: 0.")
	else:
		print("Total number of demerit points is: " + str(pointl[2])+".")

	# show option to see tickets
	choice = input("\nDo you want to see the details of tickets? \nEnter y or n: ")
	while choice not in ["n", "y"]:
		choice = input("Do you want to see the details of tickets? \nEnter y or n: ")
	if choice == 'n':
		return
	choice1 = input("Do you want to see the tickets ordered from latest to oldest?\nEnter y or n: ")
	while choice1 not in ['n','y']:
		choice1 = input("Do you want to see the tickets ordered from latest to oldest? \nEnter y or n: ")
	if choice1 == 'n':
		findticket = '''
			select tno, t.vdate, t.violation, t.fine, t.regno, v.make, v.model
			from tickets t
			left join registrations r, vehicles v
			on t.regno = r.regno
			where v.vin = r.vin and lower(r.fname) = :f and lower(r.lname) = :l
			group by tno;
		'''
	else:
		findticket = '''
			select tno, t.vdate, t.violation, t.fine, t.regno, v.make, v.model
			from tickets t
			left join registrations r, vehicles v
			on t.regno = r.regno
			where v.vin = r.vin and lower(r.fname) = :f and lower(r.lname) = :l
			group by tno
			order by t.vdate desc;
		'''		
	cursor.execute(findticket, {"f":f_name, "l":l_name})
	ticketdetail = cursor.fetchall()
	r = len(ticketdetail)//5
	s = r
	out = 'y'
	while len(ticketdetail)>0 and r>=1:
		# show at most five tickets everytime
		for item in ticketdetail[:5]:
			print("Ticket num: "+str(item[0])+"; Violation date: "+item[1]+"; Violation description: "+item[2]+"; Fine: "+str(item[3])+"; Regno: "+str(item[4])+"; Make: "+item[5]+"; Model: "+item[6]+";\n")
		ticketdetail = ticketdetail[5:]
		r = len(ticketdetail)//5
		if r==0:
			break
		out = input("Do you want to see more? Enter y or n: ")
		while out not in ['y', 'n']:
			out = input("Do you want to see more? Enter y or n: ")
		if out == 'n':
			break
	if out == 'n' or len(ticketdetail)==0:
		return
	elif s==0:
		for item in ticketdetail:
			print("Ticket num: "+str(item[0])+"; Violation date: "+item[1]+"; Violation description: "+item[2]+"; Fine: "+str(item[3])+"; Regno: "+str(item[4])+"; Make: "+item[5]+"; Model: "+item[6]+";\n")
	else:
		out = input("Do you want to see more? Enter y or n: ")
		while out not in ['y', 'n']:
			out = input("Do you want to see more? Enter y or n: ")
		if out == 'y':
			for item in ticketdetail:
				print("Ticket num: "+str(item[0])+"; Violation date: "+item[1]+"; Violation description: "+item[2]+"; Fine: "+str(item[3])+"; Regno: "+str(item[4])+"; Make: "+item[5]+"; Model: "+item[6]+";\n")
			return



def issue_a_ticket():
	global connection, cursor
	vdate = None
	violation = None
	fine = None
	# ask the user for the input
	while True:
		regno = input("Enter registration number: ")
		if regno.isdigit() is False:
			print("The input type is wrong")
			continue
		vdate = input("Enter violation date: ")

		if vdate == "":
			vdate = time.strftime("%Y-%m-%d")

		violation = input("Enter type of violation: ")
		if re.match("^[A-Za-z0-9_]*$", violation) is False:
			print("The violation type is wrong.")
			continue

		fine = input("Enter the number of fine: ")

		if fine.isdigit() is False or fine=="":
			print("The fine type is wrong.")
			continue
		else:
			break

	cursor.execute('''
	SELECT r.fname, r.lname, v.make, v.color, v.year, v.model
	FROM registrations r, vehicles v
	WHERE v.vin = r.vin
	AND r.regno = ?;''', (regno,))

	result1 = cursor.fetchall()
	if result1 == []:
		print("The regno not exists")
		return False
	for row in result1:
		print("first name: " + row[0] + "\nlast name: " + row[1])
		# print the name of the persons on the interface
	cursor.execute('''
					select MAX(tno)
					from tickets;''')
	new_tno = cursor.fetchone()

	if new_tno[0] == None:
		new = 1
	else:
		new = new_tno[0] + 1
	# generate new ticket number by finding the biggest and plus one at it.
	cursor.execute('''INSERT INTO tickets(tno, regno ,fine ,violation ,vdate) VALUES (?,?,?,?,?);''',
				   (new, regno, vdate, violation, fine))
	# update the new ticket number to the database
	connection.commit()
	print("")
	return

def find_a_car_owner():
	global connection, cursor
	p = 5
	# ask the user to input the information
	while True:
		if p < 5:
			p = 5
		make = input("Enter the name of car maker:")
		if make == "":
			p -= 1
		else:
			if make.isalpha() is False:
				print("The input type is wrong")
				continue
		model = input("Enter the model of the car:")
		if model == "":
			p -= 1
		else:
			if re.match("^[A-Za-z0-9_]*$", model) is False:
				print("The input type is wrong")
				continue

		year = input("Enter the year of the car:")
		if year == "":
			p -= 1
		else:
			if year.isdigit() is False:
				print("The input type is wrong")
				continue

		color = input("Enter the color of the car:")
		if color == "":
			p -= 1
		else:
			if color.isalpha() is False:
				print("The input type is wrong")
				continue

		plate = input("Enter the plate of the car: ")
		if plate == "":
			p -= 1
		if p == 0:
			print("You have to enter at least one value.")
			continue
		else:
			break
	m = 0
	r1 = []
	make = make.lower()
	model = model.lower()
	color = color.lower()
	plate = plate.lower()
	cursor.execute('''SELECT vin
		FROM vehicles v
		WHERE lower(make) = ?;''',(make,))
	make_vin = cursor.fetchall()
	r1.append(make_vin)

	cursor.execute('''SELECT vin
			FROM vehicles v
			WHERE lower(model) = ?;''', (model,))
	model_vin = cursor.fetchall()
	r1.append(model_vin)
	cursor.execute('''SELECT vin
				FROM vehicles v
				WHERE lower(year) = ?;''', (year,))
	year_vin = cursor.fetchall()
	r1.append(year_vin)
	cursor.execute('''SELECT vin
					FROM vehicles v
					WHERE lower(color) = ?;''', (color,))
	color_vin = cursor.fetchall()
	r1.append(color_vin)
	cursor.execute('''SELECT vin
					FROM registrations
					WHERE lower(plate) = ?;''', (plate,))
	# take all of the matching and test it whether in the database or not
	plate_vin = cursor.fetchall()
	r1.append(plate_vin)
	r2 = []
	r3 = []
	for item in r1:
		if item:
			for element in item:
				for vin in element:
					r2.append(vin)
			r3.append(r2)
		r2=[]
	len_r3 = len(r3)
	if len_r3==0:
		print("There is no match, returning to menu.")
		return
	if len_r3 == 0:
		return False
	elif len_r3 == 1:
		result = r3[0]
	elif len_r3 == 2:
		result = set(r3[0])&set(r3[1])
	elif len_r3 == 3:
		result = set(r3[0])&set(r3[1])&set(r3[2])
	elif len_r3 == 4:
		result = set(r3[0])&set(r3[1])&set(r3[2])&set(r3[3])
	else:
		result = set(r3[0])&set(r3[1])&set(r3[2])&set(r3[3])&set(r3[4])
	# 	list all of the possible cases if all the information matches with the same person.
	print("There are "+ str(len(result))+" matchings.")
	k = len(result)
	# ask the user to input one out of the five information if the matching is 4 or more
	if k >= 4:
		answer = input("What do you want to know? (make/model/year/color/plate)")
		if answer == "make":
			a = []
			for v in result:
				cursor.execute('''
					SELECT v.make 
					FROM  vehicles v
					WHERE vin=?;
					''',(v,))
				collection1 = cursor.fetchone()
				a.append(collection1[0])
			for i in a:
				print("make: " + i)
		elif answer == "model":
			a = []
			for v in result:
				cursor.execute('''
						SELECT v.model
						FROM  vehicles v
						WHERE vin=?;
						''', (v,))
				collection2 = cursor.fetchone()
				a.append(collection2[0])
			for i in a:
				print("model: "+i)
		elif answer == "year":
			a = []
			for v in result:
				cursor.execute('''
						SELECT v.year
						FROM  vehicles v
						WHERE vin=?;
						''', (v,))
				collection3 = cursor.fetchone()
				a.append(collection3[0])
			for i in a:
				print("year: "+i)
		elif answer == "color":
			a = []
			for v in result:
				cursor.execute('''
						SELECT v.color
						FROM  vehicles v
						WHERE vin=?;
						''', (v,))
				collection4 = cursor.fetchone()
				a.append(collection4[0])
			for i in a:
				print("color: "+i)
		elif answer == "plate":
			a = []
			for v in result:
				cursor.execute('''
						SELECT v.plate
						FROM  vehicles v
						WHERE vin=?;
						''', (v,))
				collection5 = cursor.fetchone()
				a.append(collection5[0])
			for i in a:
				print("plate: "+i)
		else:
			print("You did not choose the valid option, returning to menu.")
			return False
	# if the matching less than 4, print following information.
	if k<4 :
		con = []
		for i in result:
			cursor.execute('''
			select * from registrations
			where vin=?;''',(i,))
			reg = cursor.fetchall()
			if reg==[]:
				con.append(reg)

			cursor.execute('''
			SELECT v.make, v.model, v.year, v.color, r.plate, r.regdate, r.expiry, r.fname, r.lname
			FROM registrations r, vehicles v
			WHERE r.vin = v.vin and r.vin=?
			ORDER BY r.regdate desc;''',(i,))
			a = cursor.fetchone()
			con.append(a)
		for i in con:
			if i==[]:
				print("This car has no owner.")
			print("make: " + i[0] + "\nmodel: " + i[1] + "\nyear: " + str(i[2]) + "\ncolor: " + i[3]+ "\nplate: " + i[4] + "\nregistration date: " + i[5] +
		"\nexpiry date: " + i[6] + "\nfirst name: " + i[7] +"\nlast name : " + i[8] + "\n")
		# 	print all of the information on the interface
		connection.commit()
		return



def incrementYear(dateInfo):
	dateinfo = dateInfo.split("-")
	year = int(dateinfo[0])
	month = int(dateinfo[1])
	day = int(dateinfo[2])
	initial_date = date(year, month, day)

	new_date = None

	leap_year = None
	next_year = year + 1
	if (next_year % 4) == 0:
		if (next_year % 100) == 0:
			if (next_year % 400) == 0:
				leap_year = True
			else:
				leap_year = False
		else:
			leap_year = True
	else:
		leap_year = False

	if leap_year == True:
		if month > 2:
			new_date = date(initial_date.year + 1, initial_date.month, initial_date.day + 1)

		else:
			new_date = initial_date.replace(initial_date.year + 1)

	else:
		new_date = initial_date.replace(initial_date.year + 1)

	new_date = new_date.strftime("%Y-%m-%d")
	return new_date

main()