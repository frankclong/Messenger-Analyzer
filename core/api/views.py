from rest_framework.viewsets import ModelViewSet
from ..models import Post
from .serializers import PostSerializer

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer = PostSerializer