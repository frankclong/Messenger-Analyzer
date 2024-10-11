from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from data_handler.models import Contact
from ..enums import GeneralAnalysisType, ContactAnalysisType
from .serializers import GenerateAnalysisSerializer
from ..views import handle_contact_analysis, handle_general_analysis

class AnalysisOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get list of contacts and options
        general_choices=[{"id" : analysis_type.value, "value" : analysis_type.value} for analysis_type in (GeneralAnalysisType)]
        contacts = [{"id" : contact.id, "value" : contact.name} for contact in Contact.objects.filter(user=request.user)]
        contact_choices=[{"id" : analysis_type.value, "value" : analysis_type.value} for analysis_type in (ContactAnalysisType)]
        
        output = {"generalOptions" : general_choices, 
                   "contactOptions" : contact_choices,
                   "contacts" : contacts}
        return Response(output)

class GenerateAnalysisView(APIView):
    serializer_class = GenerateAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GenerateAnalysisSerializer(data=request.query_params)
        user = request.user
        if serializer.is_valid():
            isGeneral = serializer.validated_data.get('isGeneral')
            if isGeneral:
                generic_type = GeneralAnalysisType(serializer.validated_data.get('generalFormType'))
                graph = handle_general_analysis(user, generic_type)
            else:
                contact_id = serializer.validated_data.get('selectedContact', None)
                contact_type = ContactAnalysisType(serializer.validated_data.get('contactFormType'))
                graph = handle_contact_analysis(user, contact_id, contact_type)

            output = {"graph" : graph}
            return Response(output)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  