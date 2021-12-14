# Messenger-Analyzer
Parses JSON files that hold Facebook messenger data and allows user to generate graphs and trends. Download Facebook Messenger data in JSON format and enter path to inbox to use

## Software Requirements
Make sure to have <a href="https://www.python.org/downloads/" target="_blank">Python 3</a>
, [required libraries](#Required-Libraries), and <a href="https://www.freecodecamp.org/news/learn-mongodb-a4ce205e7739/" target="_blank">MongoDB</a> installed.

![alt text](./img/menu.JPG)

## Usage
```bash
python main.py
```

When running for the first time, enter the path to your Facebook messages/inbox directory of data and click "Load". Use the "Update" button when you wish to add additional data file in the future. Use the "Clean Up" button to remove duplicate messages in case of accidental load or overload. 

## Required Libraries
* pandas
* matplotlib
* seaborn
* numpy
* spacy (with en_core_web_sm model)
* pymongo

Run `pip install -r requirements.txt` to install all

## How to download Facebook Messages Data
1. After logging in to facebook.com, click the dropdown menu in the top right corner. Select "Settings & Privacy" --> "Settings"
<br>

![alt text](./img/dlfb1.JPG)
![alt text](./img/dlfb2.JPG)

2. On the left panel, select "Your Facebook Information". Then click on "View" by "Download Your Information"
<br>

![alt text](./img/dlfb3.JPG)
![alt text](./img/dlfb4.JPG)

3. Choose your date range, set the media quality to low (allows for fast download as we don't access the media files), and set the format to JSON. In the selection menu beneath, "Deselect All" then check off "Messages" 
<br>

![alt text](./img/dlfb5.JPG)

4. After the download is ready, you will be notified. Download the zip file and extract it. The data is now ready to be fed to the program!

## Major functions
### load()
Connects to local MongoDB database and creates two collections:
* contacts - each document has a name and contact_id field
* messages - collection of all messages sent and received as per the provided JSON files. Additional fields for conversation identification and dates are added

### update()
Connects to local MongoDB and adds data to the existing collections. This is almost identical to load(). Kept separate for now in case of future changes. 

### cleanup()
Connects to local MongoDB and looks through the messages collection for documents that have the same "timestamp", "sender_name", and "content". Keeps the first document and removes subsequent ones. 

### getLastMessage()
Returns the date of the last message in the database. This allows you to know which date to start at when downloading data again to update the database. Note that since Facebook does not allow you to specify the hour, it is recommended to start on the next day. Unfortunately, you will miss any messages sent the previous day after the last download. Due to addition of the `cleanup()` function, you can now start retrieving on the day returned by this function, but cleanup time may be long. 

### getName()
Determines the name of the owner of the inbox by assuming that name is the one with the highest total messages sent count. 

### main()
Launches the tkinter GUI to allow the user to select various visualizations built using Matplotlib, Pandas, and Seaborn with data queried from MongoDB. 

## Available Visualizations
Note that date filters will be added soon.
### Top 10 (n) Most Messaged
Identifies who you have exchanged the most messages with ever! WARNING: Results may surprise you
<br>

![alt text](./img/topn.png)

### Messages over time (sent and received)
Shows activity over time. May be able to identify cyclical patterns or trends. Can also see the effect of certain events on your messaging habits (e.g. Do I talk to more people during a global pandemic?)
<br>

![alt text](./img/msg_v_time.JPG)

### Messages over time with a specific contact (sent and received)
Similar to above. 
<br>

![alt text](./img/msg_v_time_contact.png)
### Hourly Distribution of sent messages
Provides information on when you are most likely to reply. Can be used to identify unhealthy patterns or habits. 
<br>

![alt text](./img/msg_dist.JPG)
### Word spectrum
For a specific contact, identify which words you are more likely to type opposed to your contact. 
<br>

![alt text](./img/word_spectrum2.JPG)

## Next Steps/Features
* Date range filter
* Explore database cleanup alternatives - currently looks through entire database for duplicates. Can we add a label to each document that represents the import whenever data is loaded? This way we can add a function that removes the last load and potentially faster query as you would not need to check docs from the same load... 
* More graphs...
* Chatbot based on your messages?
* Character encoding