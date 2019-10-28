import json
import os
import datetime
import csv
import sys
import re
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *

from contact import Contact

_ROOT_PATH_ARG = 1

# Load data 
def main():
	rootpath = sys.argv[_ROOT_PATH_ARG]
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Arrays that hold all contact data
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

	# Write data to a CSV
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
	analyze()

def analyze():
	# Plot messages over time
	# TODO: deal with missing months - currently just performs linear interpolation
	# https://stackoverflow.com/questions/44576038/insert-missing-months-rows-in-the-dataframe-in-python
	# Get contact name
	def msgsvtime():
		name_input = name_field.get()
		if name_input in df['Name'].values:
			# Filter
			filtered_df = df[df['Name'] == name_input]
			plt.figure(1)
			plt.plot(filtered_df['Date'], filtered_df['Received Words'], label = "Received")
			plt.plot(filtered_df['Date'], filtered_df['Sent Words'], label = "Sent")
			plt.legend()
			plt.title(name_input)
			plt.show()
	def top10():
		# Top 10 (or n)
		n = 10
		fig = plt.figure(figsize = [10, 5])
		ax = fig.add_axes([0.1,0.2,0.85,0.7]) 
		# Group by name, filter top 10 and sort, plot Name vs. messages
		grouped_contacts = df.groupby(df['Name'])
		grouped_contacts = grouped_contacts['Name', 'Total Messages', 'Total Words'].sum()
		grouped_contacts.sort_values(by = ['Total Messages'], ascending = [False], inplace=True)
		if len(grouped_contacts.index) > n:
			grouped_contacts = grouped_contacts[0:n-1]
		ax.bar(grouped_contacts.index, grouped_contacts['Total Messages'])
		ax.set_ylabel("Number of Messages")
		ax.set_title("Top " + str(n) + " Most Messaged")
		plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.show()
	
	def exit_program():
		exit()
		
	# Load data to DataFrame for further analysis
	df = pd.read_csv('MessageData.csv')
	# Create date column
	df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))
	df['Total Messages'] = df['Received Messages'] + df['Sent Messages']
	df['Total Words'] = df['Received Words'] + df['Sent Words']

	menu = Tk()
	menu.geometry("500x500")
	# Top 10 Button
	top10_btn = Button(menu, text="Top 10", width = 20, command = top10)
	top10_btn.place(x=150,y=100)
	# Person over time
	msgsvtime_btn = Button(menu, text="Messages over time", width = 20, command = msgsvtime)
	msgsvtime_btn.place(x=150, y=200)
	# Get input name
	name_field = Entry(menu)
	exit_btn = Button(menu, text="Exit", width = 20, command = exit_program)
	exit_btn.place(x=150, y=300)
	name_field.place(x=150, y=250)
	name_field.focus_set()
	menu.mainloop()

if __name__ == "__main__":
	main()

