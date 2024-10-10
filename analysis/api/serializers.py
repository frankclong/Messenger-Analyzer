from rest_framework import serializers

class GenerateAnalysisSerializer(serializers.Serializer):
    isGeneral = serializers.BooleanField(required=True)  
    generalFormType = serializers.CharField(required=False) 
    selectedContact = serializers.IntegerField(required=False)  
    contactFormType = serializers.CharField(required=False)