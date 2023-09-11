from django_filters import rest_framework as filters
from .models import User, Post

class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['user__username']

class PostFilter(filters.FilterSet):
    author__username = filters.CharFilter(field_name='author__user__username', lookup_expr='icontains')
    from_date = filters.DateTimeFilter(field_name='creation_date', lookup_expr='gte')
    to_date = filters.DateTimeFilter(field_name='creation_date', lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['author__username', 'from_date', 'to_date']