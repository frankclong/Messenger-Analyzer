import json
import os
import datetime
import csv
import sys
import re
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from pandas.plotting import register_matplotlib_converters
from contact import Contact
import string
import math
import seaborn as sns
import numpy as np
import spacy
import pymongo
import time
_ROOT_PATH_ARG = 1

# python main.py ./messages/inbox

# Function to load data to a database (accessing data much better than individual json files)
def load():
	# Connect to database
	client = pymongo.MongoClient()
	db = client['messenger-analyzer']
	messages = db['messages']
	contacts = db['contacts']
	rootpath = sys.argv[_ROOT_PATH_ARG]
	print(rootpath)
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Loop through all folders
	for filename in filenames:
		# Name of file is "message_1.json"
		with open(os.path.join(rootpath, filename) + "/message_1.json") as f:
			data = json.load(f)
			# Only analyze direct messages and if more than 100 messages sent
		if data["thread_type"] == "Regular" and len(data["messages"]) > 100:
			# Add contact to collection if does not exist
			print(filename.lower())
			contact_id = filename.lower()
			contact_name = data["title"]
			
			if len(list(contacts.find({'name' : contact_name}))) == 0:
				print("Adding ", contact_name)
				doc = {
					"name" : contact_name,
					"id" : filename.lower() 
				}
				contacts.insert_one(doc)
			
			#indconv = db[contact_id]
			#indconv.drop()
			#indconv.insert_many(data['messages'])

			messages_list = data['messages']

			for message_obj in messages_list:
				# Check if content exists (not vid or photo or shared links)
				# Note that some shared links include message
				message_obj['contact_id'] = contact_id
				ts= message_obj["timestamp_ms"]
				dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
				message_obj['datetime'] = dt_obj
				message_obj['year'] = dt_obj.year
				message_obj['month'] = dt_obj.month
				message_obj['day'] = dt_obj.day
				message_obj['hour'] = dt_obj.hour
			messages.insert_many(messages_list)

def getLastMessage():
	# Connect to database
	client = pymongo.MongoClient()
	db = client['messenger-analyzer']
	messages = db['messages']
	last_message = list(messages.find().sort('datetime', -1).limit(1))[0]
	print(last_message['datetime'])

# Load data 
def main():
	rootpath = sys.argv[_ROOT_PATH_ARG]
	print(rootpath)
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory
	# Arrays that hold all contact data
	name_list=[]

	# [Name][Year][Month][Day][Messages sent, messages received, words sent, words received]
	# Print to CSV: Name, Year, Month, Day, Messages sent, Messages received, Words Sent, Words Received
	c_num = -1
	# Loop through all folders
	for filename in filenames:
		# Name of file is "message_1.json"
		with open(os.path.join(rootpath, filename) + "/message_1.json") as f:
		  data = json.load(f)

		# Only analyze direct messages and if more than 100 messages sent
		if data["thread_type"] == "Regular" and len(data["messages"]) > 100:
			# 'title' is the name of contact
			contact_name = data["title"]
			name_list.append(Contact(contact_name, filename))
			c_num = c_num+ 1
			my_contact=name_list[c_num]

			for i in data["messages"]:
				# Check if content exists (not vid or photo or shared links)
				# Note that some shared links include message
				if i.get("content") and i["type"] == 'Generic':
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
		hdr = ["Name","Year","Month","Day","Hour","Received Messages", "Sent Messages","Received Words","Sent Words"]
		writer.writerow(hdr)
		for name in name_list:
			msg_data = name.get_dates()
			msg_counts = name.get_counts()
			for entry in msg_data:
				pos = msg_data.index(entry)
				row = [name.name,entry.year,entry.month,entry.day,entry.hour, msg_counts[pos][0], msg_counts[pos][1],msg_counts[pos][2],msg_counts[pos][3]]
				writer.writerow(row)

	with open('Contact_Folders'+'.csv','w', newline='', encoding='utf-8-sig') as refFile:
		writer = csv.writer(refFile)
		hdr = ["Name","Folder"]
		writer.writerow(hdr)
		for name in name_list:
			row = [name.name, name.folder_name]
			writer.writerow(row)

def analyze():
	# TODO: use OOP for plots
	# Plot messages over time
	def msgsvtime_contact():
		# Get contact name
		name_input = name_field.get()
		# Only plot if valid name
		if name_input in df['Name'].values:
			print("Getting messages for " +  name_input + "...")
			# Filter
			filtered_df = df[df['Name'] == name_input]
			# Fill missing months with 0
			filtered_df = filtered_df.set_index('Date').resample('MS').sum()
			plt.figure()
			plt.plot(filtered_df.index, filtered_df['Received Messages'], label = "Received")
			plt.plot(filtered_df.index, filtered_df['Sent Messages'], label = "Sent")
			plt.legend()
			plt.title(name_input)
			plt.show()
		else:
			print(name_input + " not found")
	def top10():
		# Top 10 (or n)
		print("Getting top 10 most messaged...")
		n = 10
		fig = plt.figure(figsize = [10, 5])
		ax = fig.add_axes([0.1,0.2,0.85,0.7]) 
		# Group by name, filter top 10 and sort, plot Name vs. messages
		#print(df.head())
		grouped_contacts = df.groupby(df['Name'])
		#print(grouped_contacts.head())
		grouped_contacts = grouped_contacts[['Name', 'Total Messages', 'Total Words']].sum()
		#print(grouped_contacts.head())

		grouped_contacts.sort_values(by = ['Total Messages'], ascending = [False], inplace=True)
		if len(grouped_contacts.index) > n:
			grouped_contacts = grouped_contacts[0:n-1]
		ax.bar(grouped_contacts.index, grouped_contacts['Total Messages'])
		ax.set_ylabel("Number of Messages")
		ax.set_title("Top " + str(n) + " Most Messaged")
		plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.show()

	def msgsvtime_all():
		print("Getting messages over time...")
		plt.figure()
		filtered_df = df.groupby(df['Date'])
		filtered_df = filtered_df.sum()
		plt.plot(filtered_df.index, filtered_df['Received Messages'], label = "Received")
		plt.plot(filtered_df.index, filtered_df['Sent Messages'], label = "Sent")
		plt.legend()
		plt.show()

	# In-depth analysis of an individual conversation
	# May need to then save all message info into contact class? 
	# Word spectrum 
	def word_spectrum():
		# Get contact name
		nlp = spacy.load('en_core_web_sm')
		rootpath = sys.argv[_ROOT_PATH_ARG]
		name_input = name_field.get()
		folder_name = folders.loc[name_input]['Folder']
		print("Getting word spectrum for " + name_input)
		with open(rootpath + folder_name + "/message_1.json") as f:
		    data = json.load(f)

		word_counts = {}
		my_count = 0
		friend_count = 0 

		# Can I add some kind of % complete indicator?
		# Only analyze direct messages and if more than 100 messages sent
		for i in data["messages"]:
		    # Check if content exists (not vid or photo or shared links)
		    # Note that some shared links include message
		    if i.get("content") and i["type"] == 'Generic':
		        # Count number of words
		        message_text = i["content"] # Message 
		        message_doc = nlp(message_text)
		        sender = i["sender_name"]
		        # Remove all punctuation
		        for token in message_doc:
		            word = str(token.lemma_).lower()
		            #print(word, token.is_stop, token.is_punct)

		            # Ignore stopwords and punctuations and pronouns
		            if (not token.is_stop) and (not token.is_punct):
		                # Left is me, right is converser
		                if sender == name_input:
		                    friend_count += 1
		                    if word in word_counts.keys():
		                        word_counts.update({word:[word_counts[word][0], word_counts[word][1] + 1]})
		                    else:
		                        word_counts[word] = [0,1]
		                else:
		                    my_count += 1
		                    if word in word_counts.keys():
		                        word_counts.update({word:[word_counts[word][0]+1, word_counts[word][1]]})
		                    else:
		                        word_counts[word] = [1,0]

		words_data = pd.DataFrame.from_dict(word_counts,orient='index')
		words_data = words_data.reset_index()
		words_data.columns = ['word','me', 'friend']
		words_data['my_norm'] = words_data['me']/my_count*1000
		words_data['friend_norm'] = words_data['friend']/friend_count*1000
		words_data['my_prop'] = words_data['my_norm']/(words_data['my_norm']+words_data['friend_norm'])
		words_data['prop_bin'] = np.floor(words_data['my_prop']*10)
		# Filter
		words_data = words_data[(words_data['friend_norm'] > 1) | (words_data['my_norm'] > 1)]
		words_data['total'] = words_data['me']+words_data['friend']
		words_data.sort_values(by = ['total'], ascending = [False], inplace=True)
		# Visual
		summ = pd.DataFrame()
		for i in range(10):
		    summ[str(i)] = words_data[words_data['prop_bin']==i]['word'].reset_index().head(10)['word']

		bins = []
		for i in range(10):
		    bins.append(','.join(word for word in words_data[words_data['prop_bin']==i]['word'].reset_index().head(5)['word'].tolist()))
		summ_df = pd.DataFrame(bins, columns = ['Words'])
		summ_df['Val'] = pd.Series([i for i in range(10)])
		summ_df.set_index('Words', inplace = True)
		fig = plt.figure(figsize = (13,5))
		ax = fig.add_axes([0.22	,0.1,0.85,0.7]) 
		sns.heatmap(summ_df)
		plt.show()
	    
	# Peak times
	def message_hours():
		print("Getting your message times...")
		hourly_totals = df.groupby('Hour').sum()
		plt.figure()
		plt.bar(hourly_totals.index, hourly_totals['Sent Messages'])
		plt.show()

	def exit_program():
	    exit()

	# Load data to DataFrame for further analysis
	df = pd.read_csv('MessageData.csv')
	# Create date column
	df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))
	df['Total Messages'] = df['Received Messages'] + df['Sent Messages']
	df['Total Words'] = df['Received Words'] + df['Sent Words']
	folders = pd.read_csv('Contact_Folders.csv', index_col = 'Name')
	register_matplotlib_converters()

	# Main Menu Layout
	menu = Tk()
	menu.geometry("450x125")
	menu.title("Messenger Analyzer")
	# Labels
	gen_lbl = Label(menu, text="General",font=("Arial Bold", 16))
	gen_lbl.grid(column=0, row=0)
	spec_lbl = Label(menu, text="Individual:",font=("Arial Bold", 16))
	spec_lbl.grid(column=1, row=0)
	# Top 10 Button
	top10_btn = Button(menu, text="Top 10 Most Messaged", width = 20, command = top10)
	top10_btn.grid(column = 0, row = 1)
	# Message times button
	hour_btn = Button(menu, text="Message Distribution by Hour", width = 20, command = message_hours	)
	hour_btn.grid(column = 0, row = 3)
	

	# Person over time
	msgsvtime_btn = Button(menu, text="Messages over time", width = 20, command = msgsvtime_contact)
	msgsvtime_btn.grid(column = 1, row = 1)
	# Get input name
	name_field = Entry(menu)
	name_field.grid(column =2 , row = 0)
	name_field.focus_set()
	# Total messages over time
	msgsvtime_btn = Button(menu, text="Total Messages over Time", width = 20, command = msgsvtime_all)
	msgsvtime_btn.grid(column = 0, row = 2)
	# Word Spectrum
	wordspec_btn = Button(menu, text="Word Spectrum", width = 20, command = word_spectrum)
	wordspec_btn.grid(column = 1,row = 2)
	# Exit button
	exit_btn = Button(menu, text="Exit", width = 20, command = exit_program)
	exit_btn.grid(column = 2, row = 4)
	menu.mainloop()

if __name__ == "__main__":
	#load()
	#getLastMessage()
	#main()
	#analyze()
