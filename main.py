import json
import os
import datetime
import csv
import sys
from contact import Contact

_ROOT_PATH_ARG = 1

def main():
	print("hello")
	rootpath = sys.argv[_ROOT_PATH_ARG]
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Arrays that hold all data
	name_list=[]

	# [Name][Year][Month][Day][Messages sent, messages received]
	# Print to CSV: Name, Year, Month, Day, Messages sent, Messages received
	c_num = -1
	for filename in filenames:
		# Name of file is "message_1.json"
		with open(rootpath + filename + "/message_1.json") as f:
		  data = json.load(f)


		# Check for group chat, "thread_type"
		if data["thread_type"] == "Regular":
			# 'title' is the name of contact
			contact_name = data["title"]
			name_list.append(Contact(contact_name))
			c_num = c_num+ 1
			my_contact=name_list[c_num]
			#print(my_contact.name)

			for i in data["messages"]:
				sender = i["sender_name"]
				ts= i["timestamp_ms"]
				dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
				
				if sender == my_contact.name:
					my_contact.add_rcvd_msg_date(dt_obj)
				else:
					my_contact.add_sent_msg_date(dt_obj)

	with open('MessageData'+'.csv','w', newline='', encoding='utf-8-sig') as csvFile:
		writer = csv.writer(csvFile)
		hdr = ["Name","Year","Month","Received Messages", "Sent Messages"]
		writer.writerow(hdr)
		nameIndex = 0
		for name in name_list:
			msg_data = name.get_dates()
			msg_counts = name.get_counts()
			for entry in msg_data:
				pos = msg_data.index(entry)
				row = [name.name,entry.year,entry.month, msg_counts[pos][0], msg_counts[pos][1]]
				writer.writerow(row)

if __name__ == "__main__":
	main()
