from django.shortcuts import render

from data_handler.models import ConversationMessage
from django.db.models import Count

from io import StringIO
from .forms import ContactAnalysisForm, GeneralAnalysisForm
from .enums import GeneralAnalysisType, ContactAnalysisType
from .general_analysis_functions import top_n, msgsvtime_all, message_hours
from .contact_analysis_functions import msgsvtime_contact, word_spectrum
from django.contrib.auth.decorators import login_required

def get_my_name():
    my_name_obj = ConversationMessage.objects.values("sender_name") \
        .annotate(count=Count("sender_name")) \
        .order_by('-count') \
        .first()
    if my_name_obj:
        return my_name_obj["sender_name"]
    else:
        return None

def render_graph(fig):
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data

def handle_general_analysis(analysis_type: GeneralAnalysisType):
    if analysis_type == GeneralAnalysisType.TOP:
        fig = top_n(10)
    elif analysis_type == GeneralAnalysisType.MESSAGES_OVER_TIME:
        fig = msgsvtime_all(get_my_name())
    elif analysis_type == GeneralAnalysisType.MESSAGES_SENT_BY_HOUR:
        fig = message_hours(get_my_name())
    else:
        return None 

    return render_graph(fig)    

def handle_contact_analysis(contact_id: int, analysis_type: ContactAnalysisType):
    if analysis_type == ContactAnalysisType.MESSAGES_OVER_TIME:
        fig = msgsvtime_contact(contact_id)
    elif analysis_type == ContactAnalysisType.WORD_SPECTRUM:
        fig = word_spectrum(contact_id)
    else:
        return None 

    return render_graph(fig)    

@login_required
def index(request):
    graph = None
    if request.method == 'POST':
        if 'submit_general_form' in request.POST:
            general_form = GeneralAnalysisForm(request.POST)
            contact_form = ContactAnalysisForm()
            if general_form.is_valid():
                analysis_type = GeneralAnalysisType[general_form.cleaned_data['analysis_type']]
                graph = handle_general_analysis(analysis_type)
        elif 'submit_contact_form' in request.POST:
            general_form = GeneralAnalysisForm()
            contact_form = ContactAnalysisForm(request.POST)
            if contact_form.is_valid():
                selected_contact = contact_form.cleaned_data['selected_contact']
                analysis_type = ContactAnalysisType[contact_form.cleaned_data['analysis_type']]
                graph = handle_contact_analysis(selected_contact, analysis_type)
    else:
        general_form = GeneralAnalysisForm()
        contact_form = ContactAnalysisForm()

    return render(request, 'analysis/index.html', {
        'general_form' : general_form,
        'contact_form' : contact_form,
        'graph' : graph,
    })