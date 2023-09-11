from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Post, Comment
from django.contrib.auth.models import User as DjangoUser
from rest_framework.authtoken.models import Token


class CustomTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = self.create_user('admin', 'admin', superuser=True)
        self.admin_user_token = self.get_or_create_token(self.admin_user)
        self.user = self.create_user('admin', 'admin', superuser=False)
        self.user_token = self.get_or_create_token(self.user)
        self.blog_user = self.create_blog_user(self.user)

    def create_user(self, username, password, superuser=False):
        user, _ = DjangoUser.objects.get_or_create(
            username=username,
            email=f"{username}@test.com",
            is_staff=True,
            is_active=True,
            is_superuser=False)
        user.set_password(password)
        user.save()
        return user

    def create_blog_user(self, django_user):
        user = User(user=django_user)
        user.save()
        return user

    def get_or_create_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token

    def create_blog_users(self, number_users):
        for item in range(0, number_users):
            self.create_blog_user(self.create_user(f'test_user_{item}', f'password_user{item}'))

    def create_blog_post(self, user):
        post = Post(content='Text post test', author_id=user.id)
        post.save()
        return post

    def create_blog_comment(self, post, text):
        comment = Comment(content=f'Test Content text {text}', post=post, author_id=post.author_id)
        comment.save()
        return comment

    def create_blog_posts(self, number_post):
        for item in range(0, number_post):
            self.create_blog_post(self.blog_user)

    def create_comments(self, post, number_comments):
        for item in range(0, number_comments):
            comment = self.create_blog_comment(post, 'item')

    def set_credential_token(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)


class UserCustomViewSetTestCase(CustomTestCase):

    def test_create_user(self):
        url = reverse('user-list')
        user_data = {
            "username": "user_1",
            "email": "user_1@example.com",
            "password": "password123"
        }
        self.set_credential_token(self.admin_user_token.key)
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2) # Two users, 1 created on setup and 1 in test.

    def test_list_users(self):
        url = reverse('user-list')
        self.create_blog_users(5)
        self.set_credential_token(self.admin_user_token.key)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6, 'Wrong number of users')# Six users, 1 created on setup and 5 in test.

    def test_follow_user(self):
        base_url = reverse('user-list')
        self.set_credential_token(self.admin_user_token.key)
        self.create_blog_users(2)
        id_user_follower = User.objects.all()[1].id
        id_user_to_follow = User.objects.all()[2].id
        # Test following process
        url = f'{base_url}{id_user_follower}/follow/{id_user_to_follow}/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test new values of following and followers
        url = base_url + f'{id_user_follower}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        following_count = response.data['following']
        self.assertEqual(following_count, 1, 'Wrong number of following response')

        url = base_url + f'{id_user_to_follow}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        followers_count = response.data['followers']
        self.assertEqual(followers_count, 1, 'Wrong number of followers response')


class PostViewSetTestCase(CustomTestCase):

    def test_list_post(self):
        url = reverse('post-list')
        self.create_blog_posts(5)
        self.set_credential_token(self.admin_user_token.key)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Post.objects.count(), 'Wrong number of posts on response')
        self.create_blog_posts(20)
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data['results']),
                         20,
                         f'Wrong number of posts on response, must be 20 but was {response.data["count"]}')

    def test_create_post(self):
        url = reverse('post-list')
        post_data = {
            # Datos para crear una publicación de prueba
            'author': self.blog_user.id,
            'content': 'Test post content',
            # Agrega otros campos según sea necesario
        }
        self.set_credential_token(self.admin_user_token.key)
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_post_details(self):
        base_url = reverse('post-list')
        user_blog = self.create_blog_user(self.create_user(f'test_user_1', f'password_user_1'))
        blog_post = self.create_blog_post(user_blog)
        self.create_comments(blog_post, 2)
        self.set_credential_token(self.admin_user_token.key)
        url = f'{base_url}{blog_post.id}/'
        response = self.client.get(url, format='json')
        self.assertIn('post_details', response.data, 'post_details key is not in response')
        self.assertIn('comments', response.data, 'comments key is not in response')
        self.assertIn('author_details', response.data, 'author_details key post_details is not in response')
        self.assertEqual(response.data['post_details']['id'], blog_post.id, 'Wrong Post information')
        self.assertEqual(response.data['author_details']['id'], user_blog.id, 'Wrong User information')

        comments_count = len(response.data['comments'])
        self.assertEqual(comments_count, 2, 'Wrong number of comments')
        self.create_comments(blog_post, 2) # ADD 2 comments more to check response limits
        response = self.client.get(url, format='json')
        comments_count = len(response.data['comments'])
        self.assertEqual(comments_count, 3, 'Wrong number of comments') # Post have 4 comments, but must be 3 in the response

    def test_list_comments(self):
        base_url = reverse('post-list')
        user_blog = self.create_blog_user(self.create_user(f'test_user_1', f'password_user_1'))
        blog_post = self.create_blog_post(user_blog)
        self.create_comments(blog_post, 6)
        self.set_credential_token(self.admin_user_token.key)
        url = f'{base_url}{blog_post.id}/comments/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6, 'Wrong number of comments on response')

    def test_create_comment(self):
        base_url = reverse('post-list')
        self.set_credential_token(self.admin_user_token.key)

        user_blog = self.create_blog_user(self.create_user(f'test_user_1', f'password_user_1'))
        blog_post = self.create_blog_post(user_blog)
        comment_data = {
            'post': blog_post.id,
            'content': 'Test text'
        }
        url = f'{base_url}{blog_post.id}/comments/'
        response = self.client.post(url, data=comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = f'{base_url}{blog_post.id}/comments/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Comment.objects.filter(post=blog_post).count(),
                         'Wrong number of comments on response')

    # Puedes agregar más pruebas según sea necesario, incluyendo pruebas para las acciones personalizadas.
