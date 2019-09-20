import json
import os
import datetime
import csv
import sys
import re
from contact import Contact

_ROOT_PATH_ARG = 1

def main():
	rootpath = sys.argv[_ROOT_PATH_ARG]
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Arrays that hold all data
	name_list=[]

	# [Name][Year][Month][Day][Messages sent, messages received, words sent, words received]
	# Print to CSV: Name, Year, Month, Day, Messages sent, Messages received, Words Sent, Words Received
	c_num = -1
	for filename in filenames:
		# Name of file is "message_1.json"
		with open(rootpath + filename + "/message_1.json") as f:
		  data = json.load(f)


		# Only analyze direct messages and if more than 100 messages sent
		if data["thread_type"] == "Regular" and len(data["messages"]) > 100:
			# 'title' is the name of contact
			contact_name = data["title"]
			name_list.append(Contact(contact_name))
			c_num = c_num+ 1
			my_contact=name_list[c_num]
			#print(my_contact.name)

			for i in data["messages"]:
				# Check if content exists (not vid or photo)
				if i.get("content"):
					# Count number of words
					num_words = 0
					message_text = i["content"] # Message 
					words = message_text.split() # Each "word" in array
					for substr in words:
						if re.search("[a-zA-Z0-9]", substr): # Count as "word" if contains letter or number
							num_words += 1 

					sender = i["sender_name"]
					ts= i["timestamp_ms"]
					dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
					
					if sender == my_contact.name:
						my_contact.add_rcvd_msg_date(dt_obj, num_words)

					else:
						my_contact.add_sent_msg_date(dt_obj, num_words)

	with open('MessageData'+'.csv','w', newline='', encoding='utf-8-sig') as csvFile:
		writer = csv.writer(csvFile)
		hdr = ["Name","Year","Month","Received Messages", "Sent Messages","Received Words","Sent Words"]
		writer.writerow(hdr)
		nameIndex = 0
		for name in name_list:
			msg_data = name.get_dates()
			msg_counts = name.get_counts()
			for entry in msg_data:
				pos = msg_data.index(entry)
				row = [name.name,entry.year,entry.month, msg_counts[pos][0], msg_counts[pos][1],msg_counts[pos][2],msg_counts[pos][3]]
				writer.writerow(row)

if __name__ == "__main__":
	main()
