import json
import os
import datetime
import sys
import re
from numpy.lib.twodim_base import tri
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Canvas, Entry, Button, PhotoImage
import tkinter.font as TkFont
from pymongo import message
import seaborn as sns
import numpy as np
import spacy
import pymongo
import time
import glob
from pathlib import Path

MY_NAME = ""

# python main.py ./messages/inbox

# Connect to database
client = pymongo.MongoClient()
db = client['messenger-analyzer']
messages = db['messages']
contacts = db['contacts']

# Function to load data to a database (accessing data much better than individual json files)
def load(fpath_field):
	rootpath = fpath_field.get()
	if not rootpath:
		print("No path provided")
		return
	print(rootpath)
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Loop through all folders
	for filename in filenames:
		# Name of file is "message_1.json"
		# As of recent update, larger datasets are split into multiple files
		filepath = os.path.join(rootpath, filename)
		message_files = glob.glob(os.path.join(filepath, "message_*.json"))
		if len(message_files) == 0:
			print("Message files not found!")
			return

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
	print("Loading complete")

def getLastMessage():
	# Connect to database
	client = pymongo.MongoClient()
	db = client['messenger-analyzer']
	messages = db['messages']
	last_message = list(messages.find().sort('datetime', -1).limit(1))[0]
	print(last_message['datetime'])

def getName():
	# Determine who sends the most messages 
	pipeline = [
		{"$group": {"_id": "$sender_name", "count": {"$sum": 1}}},
		{"$sort" : {"count": -1}}
	]
	name = list(messages.aggregate(pipeline))[0]
	return name['_id']

def update(fpath_field):
	rootpath = fpath_field.get()
	if not rootpath:
		print("No path provided")
		return
	print(rootpath)
	filenames = os.listdir(rootpath) # get all files' and folders' names in the root directory

	# Loop through all folders
	for filename in filenames:
		# Name of file is "message_1.json"
		# As of recent update, larger datasets are split into multiple files
		filepath = os.path.join(rootpath, filename)
		message_files = glob.glob(os.path.join(filepath, "message_*.json"))
		if len(message_files) == 0:
			print("Message files not found!")
			return

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
	print("Updating complete")

# Consider adding some import ID
# allows for ensuring those are different to remove duplicates and also things like removing last import
def cleanup():
	# Identify duplicates - group messages with same timestamp, sender_name
	# Note: dropDups has been deprecated from ensureIndex
	print("Cleaning...")
	pipeline = [
		{ '$group': { 
			'_id': { 'sender_name': "$sender_name", 'timestamp_ms' : '$timestamp_ms', 'content' : '$content'}, 
			'dups': { "$addToSet": "$_id" }, 
			'count': { "$sum": 1 } 
		}},
		{ '$match': { 
			'count': { "$gt": 1 }   
		}}
	]
	dups = list(messages.aggregate(pipeline,  allowDiskUse = True))

	# Remove them
	removed = 0
	for dup in dups:
		for id in dup['dups'][1:]:
			messages.delete_one({'_id' : id})
			removed += 1
	print("Removed {} duplicate messages".format(removed))

############################################################
####### 					PLOTS					########
############################################################
# TODO: use OOP for plots
# Plot messages over time
def msgsvtime_contact(name_field):
	# Get contact name
	MY_NAME = getName()
	name_input = name_field.get()
	contact = list(contacts.find({'name' : name_input}))
	# Only plot if valid name
	if len(contact) > 0:
		print("Getting messages for " +  name_input + "...")
		contact_id = contact[0]['id']
		# Fill missing months with 0 TODO: how to do this in mongo?
		# Get messages sent
		pipeline = [
			{"$match" : {"contact_id":contact_id,"sender_name" : MY_NAME}},
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
			{"$match" : {"contact_id":contact_id, "sender_name" : {'$ne': MY_NAME}}},
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
	n = 10
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
	MY_NAME = getName()
	# Get messages sent
	pipeline = [
		{"$match" : {"sender_name" : MY_NAME}},
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
		{"$match" : {"sender_name" : {'$ne': MY_NAME}}},
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
# https://stackoverflow.com/questions/4421207/how-to-get-the-last-n-records-in-mongodb
def word_spectrum(name_field):
	MY_NAME = getName()
	nlp = spacy.load('en_core_web_sm')
	name_input = name_field.get()
	contact = list(contacts.find({'name' : name_input}))
	# Only plot if valid name
	if len(contact) > 0:
		print("Getting messages for " +  name_input + "...")
		contact_id = contact[0]['id']
		# Get messages sent
		sent_pipeline = [
			{"$match" : {"contact_id":contact_id, "sender_name": MY_NAME, "type":"Generic", "content" : {"$exists":True}}},
			{"$sort" : {"timestamp_ms": -1}}
		]
		rcvd_pipeline = [
			{"$match" : {"contact_id":contact_id, "sender_name" : {"$ne": MY_NAME}, "type":"Generic", "content" : {"$exists":True}}},
			{"$sort" : {"timestamp_ms": -1}}
		]

		sent_messages = list(messages.aggregate(sent_pipeline))[:5000]
		rcvd_messages = list(messages.aggregate(rcvd_pipeline))[:5000]
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
			bins.append('\n'.join(word for word in words_data[words_data['prop_bin']==i]['word'].reset_index().head(5)['word'].tolist()))
		summ_df = pd.DataFrame(bins, columns = ['Words'])
		summ_df['Word Spectrum'] = pd.Series([i for i in range(10)])
		summ_df.set_index('Words', inplace = True)
		summ_df_t = summ_df.transpose()
		fig = plt.figure(figsize = (13,3.5))
		ax = fig.add_axes([0.1,0.35,0.8,0.55]) 
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.set_yticks([])
		#plt.bar(summ_df_t.columns, range(1,11), width=1.0, color=sns.color_palette("Blues", n_colors=10))
		plt.bar(summ_df_t.columns, [1]*10, width=1.0, color=sns.color_palette("Blues", n_colors=10))
		plt.ylabel("\n".join(name_input.split()), rotation = 0)
		#plt.ylabel("My Contact's \nWords", rotation = 0)
		ax2 = ax.twinx()
		ax2.spines['top'].set_visible(False)
		ax2.spines['right'].set_visible(False)
		ax2.spines['left'].set_visible(False)
		ax2.set_yticks([])
		plt.ylabel("\n".join(MY_NAME.split()), rotation= 0)
		#plt.ylabel("My \nWords", rotation = 0)
		plt.show()
	
# Peak times
def message_hours():
	MY_NAME = getName()
	print("Getting your message times...")
	pipeline = [
		{"$match" : {"sender_name" : MY_NAME}},
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

def test():
	nlp = spacy.load('en_core_web_sm')
	name_input = "Michael Zhou"
	contact = list(contacts.find({'name' : name_input}))
	# Only plot if valid name
	if len(contact) > 0:
		print("Getting messages for " +  name_input + "...")
		contact_id = contact[0]['id']
		# Get messages sent
		sent_query = {"contact_id":contact_id, "sender_name": MY_NAME, "type":"Generic", "content" : {"$exists":True}}
		rcvd_query = {"contact_id":contact_id, "sender_name" : {"$ne": MY_NAME}, "type":"Generic", "content" : {"$exists":True}}
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
			bins.append('\n'.join(word for word in words_data[words_data['prop_bin']==i]['word'].reset_index().head(5)['word'].tolist()))
		summ_df = pd.DataFrame(bins, columns = ['Words'])
		summ_df['Word Spectrum'] = pd.Series([i for i in range(10)])
		summ_df.set_index('Words', inplace = True)
		summ_df_t = summ_df.transpose()
		fig = plt.figure(figsize = (13,3.5))
		ax = fig.add_axes([0.1,0.35,0.8,0.55]) 
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.set_yticks([])
		#plt.bar(summ_df_t.columns, range(1,11), width=1.0, color=sns.color_palette("Blues", n_colors=10))
		plt.bar(summ_df_t.columns, [1]*10, width=1.0, color=sns.color_palette("Blues", n_colors=10))
		plt.ylabel("\n".join(name_input.split()), rotation = 0)
		ax2 = ax.twinx()
		ax2.spines['top'].set_visible(False)
		ax2.spines['right'].set_visible(False)
		ax2.spines['left'].set_visible(False)
		ax2.set_yticks([])
		plt.ylabel("\n".join(MY_NAME.split()), rotation= 0)
		plt.show()

def main():
	OUTPUT_PATH = Path(__file__).parent
	ASSETS_PATH = OUTPUT_PATH / Path("./assets")
	def relative_to_assets(path: str) -> Path:
		return ASSETS_PATH / Path(path)

	# Set up window
	# TODO: scale for smaller resolutions
	window = Tk()
	window.geometry("1154x702")
	window.configure(bg = "#FFFFFF")
	window.title("Messenger Analyzer")

	canvas = Canvas(
		window,
		bg = "#FFFFFF",
		height = 702,
    	width = 1154,
		bd = 0,
		highlightthickness = 0,
		relief = "ridge"
	)

	# Title
	canvas.place(x = 0, y = 0)
	canvas.create_text(
		256.0,
    	25.0,
		anchor="nw",
		text="Messenger Analyzer",
		fill="#0084FF",
		font=TkFont.Font(family="Helvetica",size=48,weight="bold")
	)

	# Loading/Updating database
	canvas.create_text(
		86.0,
    	147.0,
		anchor="nw",
		text="Filepath",
		fill="#0084FF",
		font=TkFont.Font(family="Helvetica",size=24,weight="bold")
	)
	entry_image_1 = PhotoImage(
		file=relative_to_assets("entry_1.png"))
	entry_bg_1 = canvas.create_image(
		651.0,
		170.5,
		image=entry_image_1
	)
	fpath_field = Entry(
		bd=0,
		bg="#FFFFFF",
		highlightthickness=0
	)
	fpath_field.place(
		x=251.5,
		y=154.0,
		width=799.0,
		height=35.0
	)
	load_button_image = PhotoImage(
		file=relative_to_assets("button_3.png"))
	load_button = Button(
		image=load_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=lambda: load(fpath_field),
		relief="flat"
	)
	load_button.place(
		x=245.0,
		y=208.0,
		width=210.0,
		height=43.0
	)

	update_button_image = PhotoImage(
		file=relative_to_assets("button_4.png"))
	update_button = Button(
		image=update_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=lambda: update(fpath_field),
		relief="flat"
	)
	update_button.place(
		x=504.0,
		y=208.0,
		width=210.0,
		height=43.0
	)

	clean_button_image = PhotoImage(
		file=relative_to_assets("button_9.png"))
	clean_button = Button(
		image=clean_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=cleanup,
		relief="flat"
	)
	clean_button.place(
		x=763.0,
		y=208.0,
		width=210.0,
		height=43.0
	)

	# Visualizations for all coversations (General)
	canvas.create_text(
		87.0,
    	284.0,
		anchor="nw",
		text="General",
		fill="#0084FF",
		font=TkFont.Font(family="Helvetica",size=24,weight="bold")
	)
	msgsvtimeall_button_image = PhotoImage(
		file=relative_to_assets("button_1.png"))
	msgsvtimeall_button = Button(
		image=msgsvtimeall_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=msgsvtime_all,
		relief="flat"
	)
	msgsvtimeall_button.place(
		x=420.0,
		y=333.0,
		width=210.0,
		height=93.0
	)

	top10_button_image = PhotoImage(
		file=relative_to_assets("button_2.png"))
	top10_button = Button(
		image=top10_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=top10,
		relief="flat"
	)
	top10_button.place(
		x=87.0,
		y=333.0,
		width=210.0,
		height=93.0
	)
	hour_button_image = PhotoImage(
		file=relative_to_assets("button_8.png"))
	hour_button = Button(
		image=hour_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=message_hours,
		relief="flat"
	)
	hour_button.place(
		x=753.0,
		y=333.0,
		width=210.0,
		height=93.0
	)

	# Visualizations for individual conversations
	canvas.create_text(
		86.0,
    	459.0,
		anchor="nw",
		text="Individual",
		fill="#0084FF",
		font=TkFont.Font(family="Helvetica",size=24,weight="bold")
	)
	canvas.create_text(
		87.0,
    	508.0,
		anchor="nw",
		text="Name",
		fill="#0084FF",
		font=TkFont.Font(family="Helvetica",size=18,weight="bold")
	)
	entry_image_2 = PhotoImage(
		file=relative_to_assets("entry_2.png"))
	entry_bg_2 = canvas.create_image(
		374.0,
		522.0,
		image=entry_image_2
	)
	name_field = Entry(
		bd=0,
		bg="#FFFFFF",
		highlightthickness=0
	)
	name_field.place(
		x=179.0,
		y=509.0,
		width=390.0,
		height=26.0
	)
	msgsvtimeind_button_image = PhotoImage(
		file=relative_to_assets("button_6.png"))
	msgsvtimeind_button = Button(
		image=msgsvtimeind_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=lambda: msgsvtime_contact(name_field),
		relief="flat"
	)
	msgsvtimeind_button.place(
		x=87.0,
		y=555.0,
		width=210.0,
		height=93.0
	)

	wordspec_button_image = PhotoImage(
		file=relative_to_assets("button_7.png"))
	wordspec_button = Button(
		image=wordspec_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=lambda: word_spectrum(name_field),
		relief="flat"
	)
	wordspec_button.place(
		x=420.0,
		y=555.0,
		width=210.0,
		height=93.0
	)
	
	# Exit program buttom
	exit_button_image = PhotoImage(
		file=relative_to_assets("button_5.png"))
	exit_button = Button(
		image=exit_button_image,
		borderwidth=0,
		highlightthickness=0,
		command=exit_program,
		relief="flat"
	)
	exit_button.place(
		x=1032.0,
		y=637.0,
		width=102.0,
		height=43.0
	)	
	window.resizable(False, False)
	window.mainloop()


if __name__ == "__main__":
	# getLastMessage()
	#test()
	main()