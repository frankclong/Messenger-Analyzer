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
import seaborn as sns
import numpy as np
import spacy
import pymongo
import time
import glob
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
		# As of recent update, larger datasets are split into multiple files
		filepath = os.path.join(rootpath, filename)
		message_files = glob.glob(os.path.join(filepath, "message_*.json"))

		for message_file in message_files:
			#basename = os.path.basename(message_file)
			with open(message_file) as f:
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

def update():
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
		# As of recent update, larger datasets are split into multiple files
		filepath = os.path.join(rootpath, filename)
		message_files = glob.glob(os.path.join(filepath, "message_*.json"))

		for message_file in message_files:
			#basename = os.path.basename(message_file)
			with open(message_file) as f:
				data = json.load(f)
			
			if data["thread_type"] == "Regular":
				# Add contact to collection if does not exist
				print(filename.lower())
				contact_id = filename.lower()
				contact_name = data["title"]
				
				if len(list(contacts.find({'name' : contact_name}))) == 0:
					print("Adding new contact ", contact_name)
					doc = {
						"name" : contact_name,
						"id" : filename.lower() 
					}
					contacts.insert_one(doc)
				else:
					print("Updating ", contact_name)
				messages_list = data['messages']
				for message_obj in messages_list:
					message_obj['contact_id'] = contact_id
					ts= message_obj["timestamp_ms"]
					dt_obj = datetime.datetime.fromtimestamp(int(ts/1000))
					message_obj['datetime'] = dt_obj
					message_obj['year'] = dt_obj.year
					message_obj['month'] = dt_obj.month
					message_obj['day'] = dt_obj.day
					message_obj['hour'] = dt_obj.hour
				messages.insert_many(messages_list)

def analyze():
	client = pymongo.MongoClient()
	db = client['messenger-analyzer']
	messages = db['messages']
	contacts = db['contacts']
	# TODO: use OOP for plots
	# Plot messages over time
	def msgsvtime_contact():
		# Get contact name
		name_input = name_field.get()
		contact = list(contacts.find({'name' : name_input}))
		# Only plot if valid name
		if len(contact) > 0:
			print("Getting messages for " +  name_input + "...")
			contact_id = contact[0]['id']
			# Fill missing months with 0 TODO: how to do this in mongo?
			# Get messages sent
			pipeline = [
				{"$match" : {"contact_id":contact_id,"sender_name" : "Frank Long"}},
				{"$group": {"_id": {"year":"$year","month":"$month"}, "count": {"$sum": 1}}},
				{"$sort" : {"_id": 1}}
			]
			messages_sent = list(messages.aggregate(pipeline))
			sent_dates = []
			sent_counts = []
			for val in messages_sent:
				# Get real name
				year = val['_id']['year']
				month = val['_id']['month']
				date = datetime.datetime(year, month, 1)
				sent_dates.append(date)
				sent_counts.append(val['count'])
			
			# Get messages received
			pipeline = [
				{"$match" : {"contact_id":contact_id, "sender_name" : {'$ne':"Frank Long"}}},
				{"$group": {"_id": {"year":"$year","month":"$month"}, "count": {"$sum": 1}}},
				{"$sort" : {"_id": 1}}
			]
			messages_rcvd = list(messages.aggregate(pipeline))
			rcvd_dates = []
			rcvd_counts = []
			for val in messages_rcvd:
				# Get real name
				year = val['_id']['year']
				month = val['_id']['month']
				date = datetime.datetime(year, month, 1)
				rcvd_dates.append(date)
				rcvd_counts.append(val['count'])

			plt.figure()
			plt.plot(rcvd_dates, rcvd_counts, label = "Received")
			plt.plot(sent_dates, sent_counts, label = "Sent")
			plt.xlabel("Date")
			plt.ylabel("Number of Messages")
			plt.legend()
			plt.title(name_input)
			plt.show()
		else:
			print(name_input + " not found")
	
	def top10():
		# Top 10 (or n)
		print("Getting top 10 most messaged...")
		n = 20
		fig = plt.figure(figsize = [10, 5])
		ax = fig.add_axes([0.1,0.2,0.85,0.7]) 
		# Group by name, filter top 10 and sort, plot Name vs. messages
		pipeline = [
			{"$group": {"_id": "$contact_id", "count": {"$sum": 1}}},
			{"$sort" : {"count": -1}}
		]
		vals = list(messages.aggregate(pipeline))[0:n]
		names = []
		message_count = []
		for val in vals:
			# Get real name
			contact = contacts.find({'id' : val['_id']})
			name = list(contact)[0]['name']
			names.append(name)
			message_count.append(val['count'])
		ax.bar(names, message_count)
		ax.set_ylabel("Number of Messages")
		ax.set_title("Top " + str(n) + " Most Messaged")
		plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.show()

	def msgsvtime_all():
		print("Getting messages over time...")
		# Get messages sent
		pipeline = [
			{"$match" : {"sender_name" : "Frank Long"}},
			{"$group": {"_id": {"year":"$year","month":"$month"}, "count": {"$sum": 1}}},
			{"$sort" : {"_id": 1}}
		]
		messages_sent = list(messages.aggregate(pipeline))
		sent_dates = []
		sent_counts = []
		for val in messages_sent:
			# Get real name
			year = val['_id']['year']
			month = val['_id']['month']
			date = datetime.datetime(year, month, 1)
			sent_dates.append(date)
			sent_counts.append(val['count'])
		
		# Get messages received
		pipeline = [
			{"$match" : {"sender_name" : {'$ne':"Frank Long"}}},
			{"$group": {"_id": {"year":"$year","month":"$month"}, "count": {"$sum": 1}}},
			{"$sort" : {"_id": 1}}
		]
		messages_rcvd = list(messages.aggregate(pipeline))
		rcvd_dates = []
		rcvd_counts = []
		for val in messages_rcvd:
			# Get real name
			year = val['_id']['year']
			month = val['_id']['month']
			date = datetime.datetime(year, month, 1)
			rcvd_dates.append(date)
			rcvd_counts.append(val['count'])

		plt.figure()
		plt.plot(rcvd_dates, rcvd_counts, label = "Received")
		plt.plot(sent_dates, sent_counts, label = "Sent")
		plt.xlabel("Date")
		plt.ylabel("Number of Messages")
		plt.legend()
		plt.title("Total Messages over Time")
		plt.show()

	# In-depth analysis of an individual conversation
	# Word spectrum 
	# Curretly very slow.. consider sampling the conversation or explore other ways of processing
	def word_spectrum():
		nlp = spacy.load('en_core_web_sm')
		name_input = name_field.get()
		contact = list(contacts.find({'name' : name_input}))
		# Only plot if valid name
		if len(contact) > 0:
			print("Getting messages for " +  name_input + "...")
			contact_id = contact[0]['id']
			# Get messages sent
			sent_query = {"contact_id":contact_id, "sender_name":"Frank Long", "type":"Generic", "content" : {"$exists":True}}
			rcvd_query = {"contact_id":contact_id, "sender_name" : {"$ne":"Frank Long"}, "type":"Generic", "content" : {"$exists":True}}
			sent_messages = list(messages.find(sent_query))
			rcvd_messages = list(messages.find(rcvd_query))
			sent_messages_joined = ' '.join(map(lambda x: x['content'], sent_messages))
			rcvd_messages_joined = ' '.join(map(lambda x: x['content'], rcvd_messages))

			# Get contact name
			word_counts = {}
			my_count = 0
			friend_count = 0 

			# Process sent messages
			message_doc = nlp(sent_messages_joined)
			# Remove all punctuation
			for token in message_doc:
				word = str(token.lemma_).lower()
				# Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
				if (not token.is_stop) and (not token.is_punct) and (len(token) > 2):
					my_count += 1
					if word in word_counts.keys():
						word_counts.update({word:[word_counts[word][0]+1, word_counts[word][1]]})
					else:
						word_counts[word] = [1,0]

			# Process rcvd messages
			message_doc = nlp(rcvd_messages_joined)
			# Remove all punctuation
			for token in message_doc:
				word = str(token.lemma_).lower()
				# Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
				if (not token.is_stop) and (not token.is_punct) and (len(token) > 2):
					# Left is me, right is converser
					friend_count += 1
					if word in word_counts.keys():
						word_counts.update({word:[word_counts[word][0], word_counts[word][1] + 1]})
					else:
						word_counts[word] = [0,1]
			
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
			summ_df['Word Spectrum'] = pd.Series([i for i in range(10)])
			summ_df.set_index('Words', inplace = True)
			fig = plt.figure(figsize = (13,5))
			ax = fig.add_axes([0.22	,0.1,0.85,0.7]) 
			sns.heatmap(summ_df)
			plt.show()
	    
	# Peak times
	def message_hours():
		print("Getting your message times...")
		pipeline = [
			{"$match" : {"sender_name" : "Frank Long"}},
			{"$group": {"_id": "$hour", "count": {"$sum": 1}}},
			{"$sort" : {"_id": 1}}
		]
		vals = list(messages.aggregate(pipeline))
		hours = range(24)
		message_count = []
		for val in vals:
			message_count.append(val['count'])
		total_messages = sum(message_count)
		message_frac = [c/total_messages for c in message_count]
		plt.figure()
		plt.bar(hours, message_frac)
		plt.ylabel("Proportion")
		plt.xlabel("Hour")
		plt.show()

	def exit_program():
	    exit()

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

def test():
	client = pymongo.MongoClient()
	db = client['messenger-analyzer']
	messages = db['messages']
	contacts = db['contacts']
	name_input = 'Daniel Lin'
	contact = list(contacts.find({'name' : name_input}))
	# Only plot if valid name
	if len(contact) > 0:
		print("Getting messages for " +  name_input + "...")
		contact_id = contact[0]['id']
		# Get messages sent
		sent_query = {"contact_id":contact_id, "sender_name":"Frank Long", "type":"Generic", "content" : {"$exists":True}}
		rcvd_query = {"contact_id":contact_id, "sender_name" : {"$ne":"Frank Long"}, "type":"Generic", "content" : {"$exists":True}}
		sent_messages = list(messages.find(sent_query))
		rcvd_messages = list(messages.find(rcvd_query))

		sent_messages_joined = ' '.join(map(lambda x: x['content'], sent_messages))
		rcvd_messages_joined = ' '.join(map(lambda x: x['content'], rcvd_messages))

		# Get contact name
		nlp = spacy.load('en_core_web_sm')
		word_counts = {}
		my_count = 0
		friend_count = 0 

		# Process sent messages
		message_doc = nlp(sent_messages_joined)
		# Remove all punctuation
		for token in message_doc:
			word = str(token.lemma_).lower()
			# Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
			if (not token.is_stop) and (not token.is_punct) and (len(token) > 2):
				my_count += 1
				if word in word_counts.keys():
					word_counts.update({word:[word_counts[word][0]+1, word_counts[word][1]]})
				else:
					word_counts[word] = [1,0]

		# Process rcvd messages
		message_doc = nlp(rcvd_messages_joined)
		# Remove all punctuation
		for token in message_doc:
			word = str(token.lemma_).lower()
			# Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
			if (not token.is_stop) and (not token.is_punct) and (len(token) > 2):
				# Left is me, right is converser
				friend_count += 1
				if word in word_counts.keys():
					word_counts.update({word:[word_counts[word][0], word_counts[word][1] + 1]})
				else:
					word_counts[word] = [0,1]


		print("Processing words...")
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

if __name__ == "__main__":
	#load()
	#getLastMessage()
	#update()
	#main()
	analyze()
	#test()