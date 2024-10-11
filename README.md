# Messenger-Analyzer
Parses JSON files that hold Facebook messenger data and allows user to generate graphs and trends. Download Facebook Messenger data in JSON format and enter path to inbox to use

## Software Requirements
Make sure to have <a href="https://www.python.org/downloads/" target="_blank">Python 3</a>
, [required libraries](#Required-Libraries), and <a href="https://nodejs.org/en" target="_blank">Node JS</a> installed.

![alt text](./static/img/menu.png)

## Usage
To start the back-end server run the following:
```bash
python manage.py runserver
```

Navigate to the `frontend` directory and run the following command to start the front-end app
```bash
npm run dev
```

## Required Libraries
Run `pip install -r requirements.txt` to install all

## How to download Facebook Messages Data
1. After logging in to facebook.com, click the dropdown menu in the top right corner. Select "Settings & Privacy" --> "Settings"
<br>

![alt text](./static/img/dlfb1.JPG)
![alt text](./static/img/dlfb2.JPG)

2. On the left panel, select "Your Facebook Information". Then click on "View" by "Download Your Information"
<br>

![alt text](./static/img/dlfb3.JPG)
![alt text](./static/img/dlfb4.JPG)

3. Choose your date range, set the media quality to low (allows for fast download as we don't access the media files), and set the format to JSON. In the selection menu beneath, "Deselect All" then check off "Messages" 
<br>

![alt text](./static/img/dlfb5.JPG)

4. After the download is ready, you will be notified. Download the zip file and extract it. The data is now ready to be fed to the program!

## Available Visualizations
Note that date filters will be added soon.
### Top 10 (n) Most Messaged
Identifies who you have exchanged the most messages with ever! WARNING: Results may surprise you
<br>

![alt text](./static/img/topn.png)

### Messages over time (sent and received)
Shows activity over time. May be able to identify cyclical patterns or trends. Can also see the effect of certain events on your messaging habits (e.g. Do I talk to more people during a global pandemic?)
<br>

![alt text](./static/img/msg_v_time.PNG)

### Messages over time with a specific contact (sent and received)
Similar to above. 
<br>

![alt text](./static/img/msg_v_time_contact.png)
### Hourly Distribution of sent messages
Provides information on when you are most likely to reply. Can be used to identify unhealthy patterns or habits. 
<br>

![alt text](./static/img/msg_dist.JPG)
### Word spectrum
For a specific contact, identify which words you are more likely to type opposed to your contact. 
<br>

![alt text](./static/img/wordspectrum.PNG)

## Major functions
Section needs updating.

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

## Next Steps/Features
* Date range filter
* More graphs...
* Chatbot based on your messages