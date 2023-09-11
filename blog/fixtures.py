import pytest
from django.contrib.auth.models import User as DjangoUser
from rest_framework.authtoken.models import Token
from blog.models import User, Post, Comment

@pytest.mark.django_db
def create_user(username, password, superuser=False):
    user, _ = DjangoUser.objects.get_or_create(
        username=username,
        email=f"{username}@test.com",
        is_staff=True,
        is_active=True,
        is_superuser=False)
    user.set_password(password)
    user.save()
    return user

@pytest.mark.django_db
def create_blog_user(username, password):
    django_user = create_user(username,password)
    blog_user = User(user=django_user)
    blog_user.save()
    return blog_user


@pytest.mark.django_db
def create_post(blog_user, content):
    post = Post(author=blog_user, content=content).save()
    return post


@pytest.mark.django_db
def create_comment(post, content, blog_user):
    post = Comment(author=blog_user, content=content, post=post).save()
    return post


@pytest.mark.django_db
def get_or_create_token(db, create_user):
   user = create_user()
   token, _ = Token.objects.get_or_create(user=user)
   return token