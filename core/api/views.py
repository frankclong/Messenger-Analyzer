from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Post
from .serializers import PostSerializer, UserSerializer
from django.contrib.auth.models import User 


# Simple
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer = PostSerializer

# Enables more cusotmization
class MyView(APIView):
    serializer_class = PostSerializer
    def get(self, request):
        output = [{"title" : output.title, "body" : output.body}
                  for output in Post.objects.all()]
        return Response(output)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]