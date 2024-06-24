from django.shortcuts import render

from data_handler.models import Contact, ConversationMessage
from django.db.models import Count

import matplotlib.pyplot as plt
from io import StringIO
import numpy as np

def get_my_name():
    my_name_obj = ConversationMessage.objects.values("sender_name") \
        .annotate(count=Count("sender_name")) \
        .order_by('-count') \
        .first()
    if my_name_obj:
        return my_name_obj["sender_name"]
    else:
        return None

FB_BLUE = (0,0.5176,1,1)
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

def render_graph(fig):
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data

def result(request):
    fig = top_n(10)
    graph = render_graph(fig)
    
    return render(request, 'analysis/result.html',
                  {
                      "graph" : graph
                  })


def index(request):
    return render(request, 'analysis/index.html')