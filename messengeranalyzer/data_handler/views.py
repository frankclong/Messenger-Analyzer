import os
import zipfile
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import MessagesDataUploadForm
import glob
import json
from .models import Contact, ConversationMessage
import datetime 
from pytz import timezone

INBOX_FOLDERS = ["inbox", "e2ee_cutover"]

# Helper functions
def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)  # Create directory if it doesn't exist
    upload_path = os.path.join(upload_dir, f.name)
    with open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return upload_path

# TODO only save the inbox folders
def extract_zip(uploaded_file_path):
    extracted_files = []
    extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted')
    os.makedirs(extract_path, exist_ok=True)  # Create directory if it doesn't exist
    with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
        extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted')
        zip_ref.extractall(extract_path)
        extracted_files = zip_ref.namelist()
    return extracted_files, extract_path

def find_specific_folder(root_dir, target_folder_name):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if target_folder_name in dirnames:
            return os.path.join(dirpath, target_folder_name)
    return None

def create_models_from_extracted_files(extracted_files, extract_path):
    tz = timezone('US/Eastern')

    for inbox_folder in INBOX_FOLDERS: 
        inbox_path = find_specific_folder(extract_path, inbox_folder)
        if not inbox_path:
            # print("Invalid path. Inbox not found")
            return

        print(inbox_path)
        filenames = os.listdir(inbox_path)
        
        # Loop through all folders
        for filename in filenames:
            # Name of file is "message_1.json"
            # As of recent update, larger datasets are split into multiple files
            filepath = os.path.join(inbox_path, filename)
            message_files = glob.glob(os.path.join(filepath, "message_*.json"))
            if len(message_files) == 0:
                # print("Message files not found!")
                return

            for message_file in message_files:
                with open(message_file, encoding="utf-8") as f:
                    data = json.load(f)
            
                # Only analyze direct messages and if more than 100 messages sent
                if len(data["messages"]) > 100:
                    # Add contact to collection if does not exist
                    # print(filename.lower())
                    contact_id = filename.lower()
                    contact_name = data["title"]

                    contact = Contact.objects.filter(folder_id=contact_id).first()

                    if not contact:
                        # print("Adding ", contact_name)
                        contact = Contact.objects.create(name=contact_name, folder_id=contact_id, ignore_conflicts=True)

                    messages_list = data['messages']
                    message_models = []

                    for message_obj in messages_list:
                        if "content" in message_obj:
                            ts = message_obj["timestamp_ms"]
                            dt_obj = datetime.datetime.fromtimestamp(int(ts/1000), tz)

                            conversation_message = ConversationMessage(
                                sender_name=message_obj["sender_name"],
                                content=message_obj["content"],
                                contact=contact,
                                timestamp_ms=ts,
                                sent_time=dt_obj
                            )
                            message_models.append(conversation_message)
                    ConversationMessage.objects.bulk_create(message_models, batch_size=500, ignore_conflicts=True)
                    

# Views
def upload_zip(request):
    if request.method == 'POST':
        form = MessagesDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file_path = handle_uploaded_file(request.FILES['file'])
            extracted_files, extract_path = extract_zip(uploaded_file_path)
            create_models_from_extracted_files(extracted_files, extract_path)
            return redirect('core:index') # TODO redirect
    else:
        form = MessagesDataUploadForm()
    return render(request, 'data_handler/upload.html', {'form': form})