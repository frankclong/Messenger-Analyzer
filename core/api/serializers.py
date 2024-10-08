from django.contrib.auth.models import User 
from rest_framework.serializers import ModelSerializer
from ..models import Post

class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'body')

class UserSerializer(ModelSerializer):
    class Meta:
        model = User 
        fields = ('id', 'username', 'password')
        extra_kwargs = {"password" : {"write_only" : True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user