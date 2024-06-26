import matplotlib.pyplot as plt
from data_handler.models import ConversationMessage
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear
import datetime
import spacy
import pandas as pd
import seaborn as sns
import numpy as np
from .query_filters import valid_message_filter

FB_BLUE = (0,0.5176,1,1)
FB_GREY = '#b6b6bc' # #b6b6bc, #cccdd4

def msgsvtime_contact(contact):
    # Get contact name
    contact_name = contact.name

    # Get messages sent	
    messages_sent = ConversationMessage.objects.filter(~Q(sender_name=contact_name) & valid_message_filter()
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
    messages_rcvd = ConversationMessage.objects.filter(Q(sender_name=contact_name) & valid_message_filter()
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
    plt.title(contact_name, fontsize = 18)
    plt.xticks()
    plt.yticks()
    return fig


# In-depth analysis of an individual conversation
# Word spectrum 
# Curretly very slow.. consider sampling the conversation or explore other ways of processing
# https://stackoverflow.com/questions/4421207/how-to-get-the-last-n-records-in-mongodb
def word_spectrum(contact):
    # Get contact name
    contact_name = contact.name
	
    nlp = spacy.load('en_core_web_sm')
    sent_messages = ConversationMessage.objects.filter(~Q(sender_name=contact_name) & valid_message_filter()
        ).values('content', 'timestamp_ms').annotate(
            count=Count('id')
        ).order_by('-timestamp_ms')[:5000]
    
    rcvd_messages = ConversationMessage.objects.filter(Q(sender_name=contact_name) & valid_message_filter()
        ).values('content', 'timestamp_ms').annotate(
            count=Count('id')
        ).order_by('-timestamp_ms')[:5000]
    
    def decode(string):
        byte_sequence = string.encode('latin1')
        return byte_sequence.decode('utf-8')

    sent_messages_joined = ' '.join(map(lambda x: decode(x['content']), sent_messages))
    rcvd_messages_joined = ' '.join(map(lambda x: decode(x['content']), rcvd_messages))

    # Get contact name
    word_counts = {}
    my_count = 0
    friend_count = 0 

    # Process sent messages
    message_doc = nlp(sent_messages_joined)
    # Remove all punctuation
    for token in message_doc:
        word = str(token.lemma_).lower().strip()
        # Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
        if (not token.is_stop) and (not token.is_punct) and (len(word) > 2): 
            my_count += 1
            if word in word_counts.keys():
                word_counts.update({word:[word_counts[word][0]+1, word_counts[word][1]]})
            else:
                word_counts[word] = [1,0]

    # Process rcvd messages
    message_doc = nlp(rcvd_messages_joined)
    # Remove all punctuation
    for token in message_doc:
        word = str(token.lemma_).lower().strip()
        # Ignore stopwords and punctuations and pronouns and short words (2 or less letters)
        if (not token.is_stop) and (not token.is_punct) and (len(word) > 2):
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
    plt.xticks(fontsize = 12)
    plt.ylabel("\n".join(contact_name.split()), rotation = 0)
    # plt.ylabel("My Contact's \nWords", rotation = 0, fontproperties = roboto_prop, fontsize = 10)
    ax2 = ax.twinx()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.set_yticks([])
    plt.ylabel("Me", rotation= 0)
    # plt.ylabel("My \nWords", rotation = 0, fontproperties = roboto_prop, fontsize = 10)
    return fig