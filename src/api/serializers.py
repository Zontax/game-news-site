from rest_framework.serializers import ModelSerializer, SlugRelatedField, SerializerMethodField
from rest_framework import serializers

from users.models import User
from posts.models import Post, PostComment


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password',
                  'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)


class UserListSerializer(ModelSerializer):
    """Список користувачів"""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')


class PostListSerializer(ModelSerializer):
    """Список всіх публікацій"""

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'created_date', 'type',
                  'user', 'image')


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
        fields = ('id', 'user', 'text', 'created_date',
                  'is_edited', 'childrens')


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
