import os
import zipfile
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import MessagesDataUploadForm

# Helper functions
def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)  # Create directory if it doesn't exist
    upload_path = os.path.join(upload_dir, f.name)
    with open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return upload_path

def extract_zip(uploaded_file_path):
    extracted_files = []
    extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted')
    os.makedirs(extract_path, exist_ok=True)  # Create directory if it doesn't exist
    with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
        extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted')
        zip_ref.extractall(extract_path)
        extracted_files = zip_ref.namelist()
    return extracted_files, extract_path

def create_models_from_extracted_files(extracted_files, extract_path):
    for file_name in extracted_files:
        file_path = os.path.join(extract_path, file_name)
        # TODO Add your logic to read the file and create models
        # with open(file_path, 'r') as file:
        #     data = file.read()
        #     # Parse the data and create Contact and Message models

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