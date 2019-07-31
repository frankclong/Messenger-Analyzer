import json
import os
import datetime
import csv

def main():

	rootpath = 'C:/Users/frank/Desktop/Messenger Analyzer/messages/inbox/'
	filenames= os.listdir (rootpath) # get all files' and folders' names in the root directory

	# Array that holds all data
	msgDataAll = []
	nameList=[]
	yearList = []
	msgCountList=[]

	# [Name][Year][Month][Day][Messages sent, messages received]
	# Print to CSV: Name, Year, Month, Day, Messages sent, Messages received
	cNum = -1
	for filename in filenames:
		# Name of file is "message_1.json"
		with open(rootpath+filename+'/message_1.json') as f:
		  data = json.load(f)

		# Check for group chat, "thread_type"
		if data["thread_type"] == "Regular":		
			# 'title' is the name of contact
			contactName = data["title"]
			nameList.append(contactName)
			cNum = cNum+ 1
			for i in data["messages"]:
				sender = i["sender_name"]
				ts = i["timestamp_ms"]
				dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
				msgYear=dt_obj.year

				# Start new list in year list
				if len(yearList) <= cNum:	
					yearList.append([msgYear])
					msgCountList.append([1])
					yearNum = 0
				# If year list already exists
				else:
					# Check if already exists
					if msgYear not in yearList[cNum]:
						yearList[cNum].append(msgYear)
						msgCountList[cNum].append(1)
						yearNum += 1
					# if same year, add 1 
					else:
						msgCountList[cNum][yearNum] += 1

			#print(cNum)
			print(nameList[cNum])
			for yr in yearList[cNum]:
				print(yr)
			for msgCount in msgCountList[cNum]:
				print(msgCount)
				


	with open('msgInfo2.csv','w', newline='', encoding='utf-8-sig') as csvFile:
		writer = csv.writer(csvFile)
		hdr = ["Name","Year","Messages"]
		writer.writerow(hdr)
		nameIndex = 0
		for name in nameList:
			for yr in yearList[nameIndex]:
				yIndex = yearList[nameIndex].index(yr)
				# Only write to file data with over 100 messages 
				if msgCountList[nameIndex][yIndex] > 100:
					row = [name, yr, msgCountList[nameIndex][yIndex]]
					writer.writerow(row)
			nameIndex += 1

if __name__ == "__main__":
	main()
