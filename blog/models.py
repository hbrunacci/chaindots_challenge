from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.utils.translation import gettext_lazy as _
from commons.models import BaseModel

class User(BaseModel):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='user_profile')
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers_users')
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following_users')

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(_("Post content's"))


class Comment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(_("Comment content's"))


# Create your models here.
