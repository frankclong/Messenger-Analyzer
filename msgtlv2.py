import json
import os
import datetime
import csv

def main():

	rootpath = 'C:/Users/frank/Desktop/Messenger Analyzer/messages/inbox/'
	filenames= os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Arrays that hold all data
	name_list=[]
	year_list = []
	msg_count_list=[]

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
			name_list.append(contact_name)
			c_num = c_num+ 1
			for i in data["messages"]:
				sender = i["sender_name"]
				ts = i["timestamp_ms"]
				dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
				msg_year=dt_obj.year

				# Start new list in year list
				if len(year_list) <= c_num:	
					year_list.append([msg_year])
					msg_count_list.append([1])
					year_num = 0
				# If year list already exists
				else:
					# Check if already exists
					if msg_year not in year_list[c_num]:
						year_list[c_num].append(msg_year)
						msg_count_list[c_num].append(1)
						year_num += 1
					# If same year, add 1 
					else:
						msg_count_list[c_num][year_num] += 1

			#print(cNum)
			print(name_list[c_num])
			for year in year_list[c_num]:
				print(year)
			for msg_count in msg_count_list[c_num]:
				print(msg_count)
				


	with open('msgInfo2.csv','w', newline='', encoding='utf-8-sig') as csvFile:
		writer = csv.writer(csvFile)
		hdr = ["Name","Year","Messages"]
		writer.writerow(hdr)
		nameIndex = 0
		for name in name_list:
			for year in year_list[nameIndex]:
				yIndex = year_list[nameIndex].index(year)
				# Only write to file data with over 100 messages 
				if msg_count_list[nameIndex][yIndex] > 100:
					row = [name, year, msg_count_list[nameIndex][yIndex]]
					writer.writerow(row)
			nameIndex += 1

if __name__ == "__main__":
	main()
