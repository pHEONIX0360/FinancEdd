from rest_framework import serializers
from socialMedia.models import Follow, Message, Post, Reaction,Comments
from adminapp.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role','short_name', 'profile_image']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Post
        fields = '__all__'
        depth = 1


class CommentsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # post = PostSerializer()
    class Meta:
        model = Comments
        exclude = ['post']
        depth = 1

class PostSerializerWithoutUser(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ['user']

class PostReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post = PostSerializerWithoutUser()   
    class Meta:
        model = Reaction
        fields = '__all__'
        depth = 1


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'image', 'description', 'created_at', 'likes_count', 'dislikes_count', 'reports_count']
        read_only_fields = ['id', 'created_at', 'likes_count', 'dislikes_count', 'reports_count']


class FollowUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower', 'following']

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)
    

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'message', 'timestamp']
        depth = 1