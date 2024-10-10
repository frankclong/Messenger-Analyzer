from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import MessagesDataUploadSerializer
from django.contrib.auth.models import User 
from rest_framework import status
from ..views import handle_uploaded_file, extract_zip, create_models_from_extracted_files, delete_data


# Enables more cusotmization
class DataUploadView(APIView):
    serializer_class = MessagesDataUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MessagesDataUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Process the uploaded file
            uploaded_file_path = handle_uploaded_file(serializer.validated_data['file'])
            extracted_files, extract_path = extract_zip(uploaded_file_path)
            create_models_from_extracted_files(extracted_files, extract_path, request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DataDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        delete_data(request)
        return Response({"message": f"Deleted data for user {request.user.username}"}, status=status.HTTP_200_OK)

