import re
from querysearch import *
from bsddb3 import db
from datetime import datetime


def getquery(mode):
	date = []
	_from = []
	_to = []
	cc = []
	bcc = []
	subject_e = []
	subject_p = []
	body_e = []
	body_p = []
	ids = []
	# ask a query
	query = input("Enter a query or press enter to quit.")
	query = query.lower()
	if query == "":
		return "quit"
	# use re to recognize the keyword, : and the value
	queryelement = re.findall('[^ ]+[ ]*(?:=|>=|<=|<|>|:)[ ]*[^ ]+', query)
	for i in range(len(queryelement)):
		# romove everything except the single terms
		query = query.replace(queryelement[i], "")
		# remove all empty space between symbol and words
		newelement = queryelement[i].replace(" ", "")
		# separate the symbol and the words by finding the pos of symbol
		pos = re.search('(?:=|>=|<=|>|<|:)', newelement)
		start = pos.start()
		end = pos.end()
		startitem = newelement[:start]
		mid = newelement[start:end]
		enditem = newelement[end:]
		# check and process the email
		if startitem in ["from", "to", "cc", "bcc"]:
			emvalid = re.match("^([a-zA-Z0-9_\.\-])+@(([a-zA-Z0-9\-])+\.)+[a-zA-Z0-9]+$",enditem)
			if emvalid == None:
				print("Invalid email address.")
				return False
			if startitem == "from":
				_from.append([startitem, mid, enditem])
			elif startitem == "to":
				_to.append([startitem, mid, enditem])
			elif startitem == "cc":
				cc.append([startitem, mid, enditem])
			else:
				bcc.append([startitem, mid, enditem])
		# check and process date
		elif startitem == "date":
			davalid = re.match("[0-9]{4}/[0-9]{2}/[0-9]{2}", enditem)
			if davalid == None:
				print("Invalid data format.")
				return False
			date.append([startitem, mid, enditem])
		# check and process subject and body terms
		elif startitem in ["subj", "body"]:
			part = re.match('[a-zA-Z0-9\_\-]+%', enditem)
			if part == None:
				if startitem == "subj":
					subject_e.append([startitem, mid, enditem])
				else:
					body_e.append([startitem, mid, enditem])
			else:
				element = enditem.replace("%", "")
				if startitem == "subj":
					subject_p.append([startitem, mid, element])
				else:
					body_p.append([startitem, mid, element])
		else:
			print("Invalid input")
			return False
	term_e = []
	term_p = []
	# check and process single terms
	if query != "":
		terms = re.findall('[a-zA-Z0-9\_\-]+%?', query)
		for term in terms:
			if re.match('[a-zA-Z0-9\_\-]+%', term):
				term1 = term.replace("%", "")
				term_p.append(term1)
			else:
				term_e.append(term)
	# search for id of date
	if date!=[] :
		temp = []
		for dates in date:
			result = searchdate(dates)
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched date")
			return False
		# use set intersection to find the common id
		daresult = set.intersection(*temp)
		if daresult == set():
			print("No matched date.")
			return False
	else:
		daresult = set()

	# search for id of exact subject term
	if subject_e != []:
		temp = []
		for subj in subject_e:
			if subj[1] != ":":
				print("Invalid input")
				return False
			result = subj_ex(subj[2]) 
			if result != False:
				temp.append(set(result))
		if temp == []:
			return False
		sue = set.intersection(*temp)
		if sue == set():
			print("No matched subject exact term")
			return False
	else:
		sue = set()

	# search for id of exact body term
	if body_e != []:
		temp = []
		for body in body_e:
			if body[1] != ":":
				print("Invalid input")
				return False
			result = body_ex(body[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No mathced body exact term")
			return False
		boe = set.intersection(*temp)
		if boe == set():
			print("No matched body exact term. ")
			return False
	else:
		boe = set()
	
	# search for id of partial subject term
	if subject_p != []:
		temp = []
		for subj in subject_p:
			if subj[1] != ":":
				print("Invalid input")
				return False
			result = subj_pa(subj[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched partial subject.")
		sup = set.intersection(*temp)
		if sup == set():
			print("No matched partial term.")
			return False
	else:
		sup = set()
	
	# search for id of partial body term
	if body_p != []:
		temp = []
		for body in body_p:
			if body[1] != ":":
				print("Invalid input")
				return False
			result = body_pa(body[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched body parial term.")
		bop = set.intersection(*temp)
		if bop == set():
			print("No matched body partial term.")
			return False	
	else:
		bop = set()

	# search for id of from email
	if _from != []:
		temp = []
		for femail in _from:
			if femail[1] != ":":
				print("Invalid input")
				return False
			result = from_email(femail[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched from email")
		fresult = set.intersection(*temp)
		if fresult == set():
			print("No matched from email")
			return False
	else:
		fresult = set()
	
	# search for id of to email
	if _to != []:
		temp = []
		for temail in _to:
			if temail[1] != ":":
				print("Invalid input")
				return False
			result = to_email(temail[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched to email")
			return False
		tresult = set.intersection(*temp)
		if tresult == set():
			print("No matched to email")
			return False
	else:
		tresult = set()
	
	# search for id of cc email
	if cc != []:
		temp = []
		for cce in cc:
			if cce[1] != ":":
				print("Invalid input")
				return False
			result = cc_email(cce[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched cc email")
		cresult = set.intersection(*temp)
		if cresult == set():
			print("No matched cc email")
			return False
	else:
		cresult = set()	 

	# search for id of bcc email
	if bcc != []:
		temp = []
		for bcce in bcc:
			if bcce[1] != ":":
				print("Invalid input.")
				return False
			result = bcc_email(bcce[2])
			if result != False:
				temp.append(set(result))
		if temp == []:
			print("No matched bcc email")
		bcresult = set.intersection(*temp)
		if bcresult == set():
			print("No matched bcc email.")
			return False
	else:
		bcresult = set()

	# search for exact term in both subject and body
	if term_e != []:
		temp = []
		for terms in term_e:
			temp1 = []
			result = subj_ex(terms)
			if result != False:
				for item in result:
					temp1.append(item)
			result = body_ex(terms)
			if result != False:
				for item in result:
					temp1.append(item)
			if temp1 != []:
				temp.append(set(temp1))
		if temp == []:
			print("No matched exact term.")
			return False
		te = set.intersection(*temp)
		if te == set():
			print("No matched exact term")
			return False
	else:
		te = set()
	
	# search for partial term in both subject and body
	if term_p != []:
		temp = []
		for terms in term_p:
			temp1 = []
			result = subj_pa(terms)
			if result != False:
				for item in result:
					temp1.append(item)
			result = body_pa(terms)
			if result != False:
				for item in result:
					temp1.append(item)
			if temp1 != []:
				temp.append(set(temp1))
		if temp == []:
			print("No matched partial term.")
			return False
		tp = set.intersection(*temp)
		if tp == set():
			print("No matched partial term")
			return False
	else:
		tp = set()

	# find the intersection of all condition and search for the id
	for item in [daresult,sue, boe, sup, fresult, tresult, cresult, bcresult, te, tp]:
		if item != set():
			ids.append(item)
	if ids == []:
		print("No matched data.")
		return False
	rowid = set.intersection(*ids)

	# depend on different mode, print different output
	output = []
	if mode == "output=brief":
		for id in rowid:
			subjs = searchid(id)
			for subj in subjs:
				output.append([id, subj])
		for pairs in output:
			if pairs[1] == "":
				print("ID is: " + pairs[0] +"\nSubject is empty." )
			else:
				print("ID is: " + pairs[0] +"\nSubject is: " + pairs[1])
	elif mode == "output=full":
		for id in rowid:
			records = searchfull(id)
			for record in records:
				print("Row id: "+id)
				print("Record: "+ record)			

def main():
	mode = "output=brief" #set defult mode
	while True:	
		while True:
			mo = input("Enter output=full/output=brief(press enter to use default): ")
			mo = mo.lower()
			# set new mode
			if mo == "output=full":
				mode = "output=full"
				break
			elif mo == "output=brief":
				mode = "output=brief"
				break
			elif mo == "":
				break
		result = getquery(mode)
		if result == "quit":
			print("Quiting..")
			break
	return

main()
