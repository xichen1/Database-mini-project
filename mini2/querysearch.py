import re
from bsddb3 import db
from datetime import datetime
# search for only id and subject
def searchid(id):
    result = []
    database = db.DB()
    database.open("re.idx", None, db.DB_HASH,db.DB_CREATE)
    curs = database.cursor()
    iter = curs.first()
    # traverse the database from first to last
    while iter:
        current_id = iter[0].decode("utf-8")
        if current_id == id:
        	# use re to find the subject
            temp = re.search("<subj>(.*)</subj>", iter[1].decode("utf-8"))
            subj = temp.group(1)
            result.append(subj)
        iter = curs.next()
    curs.close()
    database.close()
    return result
# serch for id and the whole records
def searchfull(id):
    result = []
    database = db.DB()
    database.open("re.idx", None, db.DB_HASH, db.DB_CREATE)
    curs = database.cursor()
    iter = curs.first()
    # traverse the database
    while iter != None:
        current_id = iter[0].decode("utf-8")
        if current_id == id:
            result.append(iter[1].decode("utf-8"))
        iter = curs.next()
    curs.close()
    database.close()
    return result

# search for the id about the date
def searchdate(date):
    database = db.DB()
    database.open("da.idx", None, db.DB_BTREE,db.DB_CREATE)
    curs = database.cursor()
    id = []
    item = curs.first()
    # traverse the database
    while item != None:
        current_date = item[0].decode("utf-8") 
        # use strptime to change the date to be comparable
        current_date = datetime.strptime(current_date, "%Y/%m/%d")
        userdate = datetime.strptime(date[2], "%Y/%m/%d")
        # compare the date
        if date[1] == "<":
            if current_date < userdate:
                id.append(item[1].decode("utf-8"))
        elif date[1] == ">":
            if current_date > userdate:
                id.append(item[1].decode("utf-8"))
        elif date[1] == ":":
            if current_date == userdate:
                id.append(item[1].decode("utf-8"))
        elif date[1] == "<=":
            if current_date <= userdate:
                id.append(item[1].decode("utf-8"))
        elif date[1] == ">=":
            if current_date >= userdate:
                id.append(item[1].decode("utf-8"))
        else:
            return False
        item = curs.next()
    curs.close()
    database.close()
    # when finding nothing, return False
    if id == []:
        return False
    return(id)

# search for the id about the exact body term
def body_ex(term):
    
    database = db.DB()
    database.open("te.idx")
    cur = database.cursor()
    
    item = cur.first()
    row_id = []
  
    item = cur.first()
    # traverse the database
    while item != None:
        key = item[0].decode("utf-8")
        match = term
        # add b- before term to compare
        match = "b-" + term
        if match == key:
            row_id.append(item[1].decode("utf-8"))
                
        item = cur.next()
        
    
    cur.close()
    database.close()
    if row_id == []:
        return False
    return(row_id)

# search for the id about the exact subject term
def subj_ex(term):
    
    database = db.DB()
    database.open("te.idx")
    cur = database.cursor()
    
    item = cur.first()
    row_id = []
  
    item = cur.first()
    while item != None:
        key = item[0].decode("utf-8")
        match = term
        match = "s-" + term
        if match == key:
            row_id.append(item[1].decode("utf-8"))
                
        item = cur.next()
    cur.close()
    database.close()    
    if row_id == []:
        return False
    return(row_id)

# search for the id about the partial subject term
def subj_pa(term):
    
    database = db.DB()
    database.open("te.idx")
    cur = database.cursor()
    
    item = cur.first()
    row_id = []
  
    item = cur.first()
    while item != None:
        key = item[0].decode("utf-8")
        match = term
        prefix = "s-" + term
        if re.match(prefix, key):
            row_id.append(item[1].decode("utf-8"))
        item = cur.next()
        
    cur.close()
    database.close()    
    if row_id == []:
        return False
    return(row_id)

# search for the id about the partial body term
def body_pa(term):
    database = db.DB()
    database.open("te.idx")
    cur = database.cursor()
    
    item = cur.first()
    row_id = []
  
    item = cur.first()
    while item != None:
        key = item[0].decode("utf-8")
        prefix = "b-" + term
        if re.match(prefix, key):
            row_id.append(item[1].decode("utf-8"))
        
        item = cur.next()
        
    cur.close()
    database.close()    
    if row_id == []:
        return False 
    return row_id

# search for the id about the from email
def from_email(email):
    
    database = db.DB()
    database.open("em.idx")
    cur = database.cursor()
    
    item = cur.first()
    row_id = []
  
    item = cur.first()
    while item != None:
        key = item[0].decode("utf-8")
        match = email
        match = "from-" + match
        
        if match == key:
            row_id.append(item[1].decode("utf-8"))
                
        item = cur.next()
        
  
    cur.close()
    database.close()
    if row_id == []:
        return False
    return(row_id)

# search for the id about the to email
def to_email(email):
    DB_File = "em.idx"
    database = db.DB()
    database.set_flags(db.DB_DUP)
    database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
    cursor = database.cursor()
    # initializ the database and the cursor

    iter = cursor.first()
    email = "to-" + email
    list1 = []
    # add bcc as indicator to check the corresponding email

    while iter:
        email1 = iter[0].decode("utf-8")
        if email1 == email:
            list1.append(iter[1].decode("utf-8"))
        # iterate the whole database and append it into the list

        iter = cursor.next()
    if list1 == []:
        return False
    # return false if no result has been selected

    return list1
    # return the information to the main function

# search for the id about the cc email
def cc_email(email):
    DB_File = "em.idx"
    database = db.DB()
    database.set_flags(db.DB_DUP)
    database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
    cursor = database.cursor()
    # initializ the database and the cursor
    iter = cursor.first()
    email = "cc-" + email
    list1 = []
    # add bcc as indicator to check the corresponding email

    while iter:
        email1 = iter[0].decode("utf-8")
        if email1 == email:
            list1.append(iter[1].decode("utf-8"))
        # iterate the whole database and append it into the list

        iter = cursor.next()
    if list1 == []:
        return False
    # return false if no result has been selected

    return list1
    # return the information to the main function

# search for the id about the bcc email
def bcc_email(email):
    DB_File = "em.idx"
    database = db.DB()
    database.set_flags(db.DB_DUP)
    database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
    cursor = database.cursor()
    # initializ the database
    iter = cursor.first()
    email = "bcc-" + email
    # add bcc as indicator to check the corresponding email
    list1 = []
    while iter:
        email1 = iter[0].decode("utf-8")
        if email1 == email:
            list1.append(iter[1].decode("utf-8"))
        iter = cursor.next()
        # iterate the whole database and append it into the list
    if list1 == []:
        return False
    # return false if no result has been selected
    return list1
    # return the information to the main function