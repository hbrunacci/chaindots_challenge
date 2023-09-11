from rest_framework import serializers
from .models import User, Post, Comment
from django.contrib.auth.models import User as DjangoUser


class DjangoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name']  # Agrega todos los campos necesarios
        extra_kwargs = {
            'password': {'write_only': True},  # Para que el campo de contraseña no se muestre en las respuestas
        }

class UserSerializer(serializers.ModelSerializer):
    user = DjangoUserSerializer(required=False, read_only=True)
    posts = serializers.SerializerMethodField(required=False, read_only=True)
    comments = serializers.SerializerMethodField(required=False, read_only=True)
    followers = serializers.SerializerMethodField(required=False, read_only=True)
    following = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def get_posts(self, item):
        return item.posts.count()

    def get_comments(self, item):
        return item.comments.count()

    def get_followers(self, item):
        return item.followers.count()

    def get_following(self, item):
        return item.following.count()


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'