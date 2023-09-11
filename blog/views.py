from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer, DjangoUserSerializer
from commons.paginations import CustomPagination
from rest_framework.permissions import IsAuthenticated
from .filters import PostFilter


class UserCustomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    queryset = User.objects.all().prefetch_related('followers', 'following')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user__username']
    search_fields = ['user__username']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = DjangoUserSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            new_user = serializer.save()
            new_user.set_password(password)
            new_user.save()
            try:
                new_custom_user = User(user=new_user).save()
                serializer = UserSerializer(new_custom_user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                new_user.delete()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post'],
            url_path='follow/(?P<user_pk>[^/.]+)')
    def follow(self, request, pk=None, user_pk=None):
        """
        Follow a User.
        """
        user = self.get_object()
        user_to_follow = User.objects.get(id=user_pk)
        if not user_to_follow:
            return Response('Unknown User, Cannot be followed', status=status.HTTP_400_BAD_REQUEST)
        if user_to_follow in user.following.all():
            return Response('The user is already being followed.', status=status.HTTP_400_BAD_REQUEST)
        user.following.add(user_to_follow)
        user_to_follow.followers.add(user)
        user.save()
        return Response({'message': f'You are now following {user_to_follow.user.username}'})

    @action(detail=True, methods=['get'])
    def user_details(self, request, pk=None):
        """
        Get User Details.
        """
        user = self.get_object()
        total_posts = user.post_set.count()
        total_comments = user.comment_set.count()
        followers = user.followers.count()
        following = user.following.count()
        data = {
            'user_details': UserSerializer(user).data,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'followers': followers,
            'following': following,
        }
        return Response(data)


class PostViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    queryset = Post.objects.all().select_related('author__user').order_by('-creation_date')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PostFilter
    pagination_class = CustomPagination


    def create(self, request, *args, **kwargs):
        user = request.data.get('author', None)
        if not user:
            user = request.user
            if not user.user_profile:
                Response("The user haven't a profile.", status=status.HTTP_400_BAD_REQUEST)
            request.data.update({'author': user.user_profile.id})
        return super(PostViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        comments = Comment.objects.filter(post=post).select_related('author__user').order_by('-creation_date')[:3]
        data = {
            'post_details': PostSerializer(post).data,
            'comments': CommentSerializer(comments, many=True).data,
            'author_details': UserSerializer(post.author).data,
        }
        return Response(data)

    @action(detail=True,
            methods=['get', 'post'],
            url_path='comments')
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            user = request.user
            data = request.data
            data['post'] = post.id
            if not data.get('author', None):
                data['author'] = user.user_profile.id
            serializer = CommentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        queryset = Comment.objects.filter(post=post).select_related('author__user').order_by('-creation_date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)



