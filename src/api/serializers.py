from rest_framework.serializers import ModelSerializer, SlugRelatedField, SerializerMethodField

from users.models import User
from posts.models import Post, PostComment


class UserListSerializer(ModelSerializer):
    """Список користувачів"""
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')


class PostListSerializer(ModelSerializer):
    """Список всіх публікацій"""
    
    class Meta:
        model = Post
        fields = ('title', 'content', 'created_date', 'type', 'user')


class RecursiveSerializer(ModelSerializer):
    """Рекурсивний вивід childrens"""
    
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class PostCommentSerializer(ModelSerializer):
    """Дані коментаря"""
    
    user = SlugRelatedField(slug_field='username', read_only=True)
    childrens = RecursiveSerializer(many=True)
    
    class Meta:
        model = PostComment
        fields = ('user', 'text', 'created_date', 'is_edited', 'childrens')


class PostDetailSerializer(ModelSerializer):
    """Дані однієї публікації"""
    
    type = SlugRelatedField(slug_field='name', read_only=True)
    tags = SlugRelatedField(slug_field='name', read_only=True, many=True)
    likes_count = SerializerMethodField()
    dislikes_count = SerializerMethodField()
    saves_count = SerializerMethodField()
    comments = SerializerMethodField()

    class Meta:
        model = Post
        exclude = ('likes', 'dislikes', 'saves')


    def get_likes_count(self, obj: Post):
        return obj.likes.count()

    
    def get_dislikes_count(self, obj: Post):
        return obj.dislikes.count()


    def get_saves_count(self, obj: Post):
        return obj.saves.count()


    def get_comments(self, obj: Post):
        comments = obj.comments.all()
        return PostCommentSerializer(comments, many=True).data
    