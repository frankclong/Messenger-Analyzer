
import matplotlib.pyplot as plt
from data_handler.models import Contact, ConversationMessage
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractHour
import datetime
import pytz
from .query_filters import valid_message_filter

# This class contains functions that are called by views.handle_general_analysis.
# Each function should return a matplotlib fig

FB_BLUE = (0,0.5176,1,1)
FB_GREY = '#b6b6bc' # #b6b6bc, #cccdd4

def top_n(n):
    fig = plt.figure(figsize = [10, 5])
    ax = fig.add_axes([0.1,0.2,0.85,0.7]) 

    query = ConversationMessage.objects.all().values("contact") \
        .annotate(count=Count("contact")) \
        .order_by('-count')
    top_messaged = query[:n]

    names = []
    message_count = []
    for val in top_messaged:
        # Get real name
        contact_id = val['contact']
        contact = Contact.objects.filter(id=contact_id).first()
        name = contact.name
        names.append(name)
        message_count.append(val['count'])
    ax.bar(names, message_count, color = FB_BLUE)
    ax.set_ylabel("Number of Messages")
    ax.set_title("Top " + str(n) + " Most Messaged", fontsize = 18)
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.xticks()
    plt.yticks()

    return fig

def msgsvtime_all(my_name):
	# Get messages sent	
	messages_sent = ConversationMessage.objects.filter(Q(sender_name=my_name) & valid_message_filter()
        ).annotate(
			year=ExtractYear('sent_time'),
			month=ExtractMonth('sent_time'),
        ).values('year', 'month').annotate(
			count=Count('id')
		).order_by('year', 'month')
	sent_dates = []
	sent_counts = []
	for val in messages_sent:
		year = val['year']
		month = val['month']
		date = datetime.datetime(year, month, 1)
		sent_dates.append(date)
		sent_counts.append(val['count'])
	
	# Get messages received
	messages_rcvd = ConversationMessage.objects.filter(~Q(sender_name=my_name) & valid_message_filter()
		).annotate(
			year=ExtractYear('sent_time'),
			month=ExtractMonth('sent_time'),
        ).values('year', 'month').annotate(
			count=Count('id')
		).order_by('year', 'month')
	
	rcvd_dates = []
	rcvd_counts = []
	for val in messages_rcvd:
		year = val['year']
		month = val['month']
		date = datetime.datetime(year, month, 1)
		rcvd_dates.append(date)
		rcvd_counts.append(val['count'])

	fig = plt.figure(figsize = [10, 5])
	plt.plot(rcvd_dates, rcvd_counts, label = "Received", color = FB_GREY)
	plt.plot(sent_dates, sent_counts, label = "Sent", color = FB_BLUE)
	plt.xlabel("Date")
	plt.ylabel("Number of Messages")
	plt.legend()
	plt.title("Total Messages over Time", fontsize = 18)
	plt.xticks()
	plt.yticks()
	
	return fig
	
def message_hours(my_name):
	def convert_utc_hr_to_local(utc_hr):
		utc_now = datetime.datetime.utcnow()
		utc_time = utc_now.replace(hour=utc_hr, minute=0, second=0, microsecond=0)
		utc_time = pytz.utc.localize(utc_time)
		local_tz = pytz.timezone('US/Eastern')
		local_time = utc_time.astimezone(local_tz)
		return local_time.hour


	vals = ConversationMessage.objects.filter(Q(sender_name=my_name) & valid_message_filter()
            ).annotate(
                hour=ExtractHour('sent_time')
            ).values('hour').annotate(
				count=Count('id')
            ).order_by(
				'hour'
            )
	
	hours = range(24)
	message_count = {}
	total_messages_count = 0
	for val in vals:
		count = val['count']
		message_count[convert_utc_hr_to_local(val['hour'])] = count
		total_messages_count += count

	message_frac = [message_count[hour]/total_messages_count for hour in hours]
	fig = plt.figure(figsize = [10, 5])
	plt.bar(hours, message_frac, color = FB_BLUE)
	plt.ylabel("Proportion")
	plt.xlabel("Hour")
	plt.xticks()
	plt.yticks()
	return fig