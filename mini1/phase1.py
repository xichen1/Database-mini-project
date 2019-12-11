import re
import os
def date(name):
    id_list = []
    date_list = []
    with open(name, 'r', encoding='utf-8') as f:
		# open the file
        file = f.readlines()
        for lines in file[2: -1]:
            id = re.search('<row>(.*)</row>',lines)
            date = re.search('<date>(.+?)</date>',lines)
			# select the information between markers in text
            id_list.append(id)

            date_list.append(date)
	# 		add the extract information to the list
    with open("dates.txt", 'w', encoding='utf-8') as a:
		# create a new text to store the extract information
        x = 0
        for i in date_list:
                a.write(i.group(1) + ':' + id_list[x].group(1) + '\n')
                x += 1
				# write the information to the new text

def recs(name):
    id_list = []
    content_list = []

    with open(name, 'r', encoding='utf-8') as f:
		# open the file

        file = f.readlines()
        for lines in file[2: -1]:
            id = re.search('<row>(.*)</row>',lines)
            id_list.append(id)
		# select the corresponding id from the text
        for lines in file[2: -1]:
            content = re.search('<mail>(.*)</mail>',lines)
            content_list.append(content)
			# select the information between markers in text

    with open("recs.txt", 'w', encoding='utf-8') as a:
        x = 0
        for i in id_list:
            a.write(i.group(1) +':' + content_list[x].group(0) +"\n" )
            x += 1
# 	write the extract information to the new text

def email(name):
	f = open(name,'r')
	lines = f.readlines()
	record = []
	# open the file
	for line in lines:
		record.append(line)
	# append all the text into another list
	record.pop(0)
	record.pop(0)
	record.pop(-1)

	if (len(record)) == 0:
		return
	# if the text is empty, end the function
	newrecord = []
	for item in record:
		endpos = item.find("<body>")
		if endpos == -1:
			endpos = item.find("<>")
		item = item[:endpos]
		newrecord.append(item)
	# extract the information from the text
	result = []
	for item in newrecord:
		info = []
		froma = item[item.find("<from>")+len("<from>"):item.rfind("</from>")]
		info.append([froma])
		if item.find("<to>") == -1 and item.find("</to>") == -1:
			# extract the text between two indicators

			info.append([""])
		else:
			to = []
			toa = item[item.find("<to>")+len("<to>"):item.rfind("</to>")]
			if "," in toa:
				num = toa.count(",")
				for i in range(num):
					to.append(toa[:toa.find(",")])
					toa = toa[toa.find(",")+1:]
				to.append(toa)
			# 	extract information with ","
			else:
				to.append(toa)
			info.append(to)

		if item.find("<cc>") == -1 and item.find("</cc>") == -1:
			info.append([""])
			# extract the text between two indicators

		else:
			cc = []
			cca = item[item.find("<cc>")+len("<cc>"):item.rfind("</cc>")]

			if "," in cca:
				num = cca.count(",")
				for i in range(num):
					cc.append(cca[:cca.find(",")])
					cca = cca[cca.find(",")+1:]
				cc.append(cca)
			else:
				cc.append(cca)
			info.append(cc)
			# 	extract information with ","

		if item.find("<bcc>") == -1 and item.find("</bcc>") == -1:
			info.append([""])
			# extract the text between two indicators

		else:
			bcc = []
			bcca = item[item.find("<bcc>")+len("<bcc>"):item.rfind("</bcc>")]
			if "," in bcca:
				num = bcca.count(",")
				for i in range(num):
					bcc.append(bcca[:bcca.find(",")])
					bcca = bcca[bcca.find(",")+1:]
				bcc.append(bcca)
			else:
				bcc.append(bcca)
			info.append(bcc)
			# 	extract information with ","


		rowid = item[item.find("<row>")+len("<row>"):item.rfind("</row>")]
		info.append(rowid)
		result.append(info)
		# extract the text between two indicators

	for i in range(len(result)):
		for j in range(len(result[i][0])):
			result[i][0][j] = "from-" + result[i][0][j] + ":"
		if result[i][1] != [""]:
			for j in range(len(result[i][1])):
				result[i][1][j] = "to-" + result[i][1][j] + ":"
		if result[i][2] != [""]:
			for j in range(len(result[i][2])):
				result[i][2][j] = "cc-" + result[i][2][j] + ":"
		if result[i][3] != [""]:
			for j in range(len(result[i][3])):
				result[i][3][j] = "bcc-" + result[i][3][j] + ":"
		# add the string format for the output
	g = open("emails.txt", 'w')
	for items in result:
		for i in range(len(items)-1):
			for address in items[i]:
				if address != "":
					g.write(address+items[-1]+"\n")
	# write the information to the file

	f.close()
	g.close()

def terms(name):

    f = open(name, 'r')
    r = f.readlines()
    lenr = len(r)
    r = r[2:lenr-1]
    w = open("terms.txt", 'w')
	# open the input file
    for line in r:
        rowid = re.search("<row>(.*)</row>",line)
        subja = re.search("<subj>(.*)</subj>", line)
        bodya = re.search("<body>(.*)</body>", line)
        subj = subja.group(1)
        ida = rowid.group(1)
        body = bodya.group(1)
		# Extracts the corresponding information from the text between 2 markers
        for item in ["&#10", "&lt", "&gt", "&amp", "&apos", "&quot"]:
            subj = subj.replace(item, " ")
            body = body.replace(item, " ")
        for letter in subj:
            if (not letter.isalpha()) and (not letter.isdigit()) and letter != "-" and letter != "_" and letter != " ":
                subj = subj.replace(letter, " ")
        for letter in body:
            if (not letter.isalpha()) and (not letter.isdigit()) and letter != "-" and letter != "_" and letter != " ":
                body = body.replace(letter, " ")
		# swap irrelevent characters and punctuations with space
        splitsubj = subj.split()
        splitbody = body.split()
        newsubj = []
        newbody = []
        for item in splitsubj:
            if len(item) > 2:
                newsubj.append(item)
        for item in splitbody:
            if len(item) > 2:
                newbody.append(item)
        if newbody == [] and newsubj == []:
            continue
        for item in newsubj:
            item = item.lower()
            w.write("s-"+item+":"+ida+"\n")
        for item in newbody:
            item = item.lower()
            w.write("b-"+item+":"+ida+"\n")

		# regulate the format of string

def main():
	os.system("rm -f recs.txt")
	os.system("rm -f terms.txt")
	os.system("rm -f emails.txt")
	os.system("rm -f dates.txt")
	# remove the original text in order to execute opeartion
	filename = input("Enter the file name: ")
	# read the file name
	date(filename)
	recs(filename)
	email(filename)
	terms(filename)



main()





