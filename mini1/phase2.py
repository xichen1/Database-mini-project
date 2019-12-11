import os
def main():
	# empty the folder for the preparation
	os.system("rm -f re.idx")
	os.system("rm -f te.idx")
	os.system("rm -f em.idx")
	os.system("rm -f da.idx")

	# sort the txt files
	os.system("sort -u recs.txt -o re.txt")
	os.system("sort -u terms.txt -o terms.txt")
	os.system("sort -u emails.txt -o emails.txt")
	os.system("sort -u dates.txt -o dates.txt")

	# use perl program to break the txt files
	os.system("perl break.pl < recs.txt > recsTemp.txt")
	os.system("perl break.pl < terms.txt > termsTemp.txt")
	os.system("perl break.pl < emails.txt > emailsTemp.txt")
	os.system("perl break.pl < dates.txt > datesTemp.txt")

	# put the data into the .idx files
	os.system("db_load -c duplicates=0 -T -t hash -f recsTemp.txt re.idx")
	os.system("db_load -c duplicates=1 -T -t btree -f termsTemp.txt te.idx")
	os.system("db_load -c duplicates=1 -T -t btree -f emailsTemp.txt em.idx")
	os.system("db_load -c duplicates=1 -T -t btree -f datesTemp.txt da.idx")

main()
