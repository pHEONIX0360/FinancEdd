# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from socialMedia.serializer import CreatePostSerializer, FollowUsersSerializer, MessageSerializer, PostReactionSerializer, PostSerializer, UserSerializer,CommentsSerializer
from .models import Follow, Post, Reaction, PostReaction, Message, Comments
from adminapp.models import User,Student
from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.shortcuts import redirect

@csrf_exempt
def toggle_reaction(request):
    if request.method == 'POST':
        userId = request.session['userId']
        post_id = request.POST.get('post_id')
        reaction_type = request.POST.get('reaction_type')  # Assuming you have different types of reactions

        # Toggle reaction logic
        reaction, created = Reaction.objects.get_or_create(user_id=userId, post_id=post_id, reaction=reaction_type)
        if not created:
            reaction.delete()
            reacted = False
            update_post = Post.objects.get(id=post_id)
            update_post.likes_count = F('likes_count') - 1 
            update_post.save()
        else:
            reacted = True
            update_post = Post.objects.get(id=post_id)
            update_post.likes_count = F('likes_count') + 1 
            update_post.save()

        # Return the new number of likes for the post
        post = Post.objects.get(id=post_id)
        likes_count = Reaction.objects.filter(post=post).count()

        return JsonResponse({'reacted': reacted, 'likes_count': likes_count})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def post_list(request):
    try:
        userId = request.session['userId']
    except KeyError:
        return redirect('signup')
    if not userId:
        return redirect('signup')
    posts = Post.objects.all()
    users = User.objects.all()
    user_reactions = Reaction.objects.filter(user_id=userId)
    
    reacted_post_ids = set(user_reactions.values_list('post_id', flat=True))
    print(reacted_post_ids)

    return render(request, 'socialmedia.html', {
        'posts': posts,
        'reacted_post_ids': reacted_post_ids,
        'users': users,
        'userId': userId,
        'reactionCheck' : checkReactionType
    })

def checkReactionType(post, userId):
    # userId = request.session['userId']
    post_reactions = Reaction.objects.filter(post=post,user_id = userId)
    if post_reactions.exists():
        return post_reactions.first().reaction
    else:
        return None

@login_required
def follow_user(request, user_id):
    if request.method == 'POST':
        following = get_object_or_404(User, id=user_id)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
        if created:
            return JsonResponse({'message': 'Successfully followed user.'})
        else:
            return JsonResponse({'message': 'You are already following this user.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        following = get_object_or_404(User, id=user_id)
        Follow.objects.filter(follower=request.user, following=following).delete()
        return JsonResponse({'message': 'Successfully unfollowed user.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@api_view(['GET'])
def listPosts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def listReactions(request):
    reactions = Reaction.objects.all()
    serializer = PostReactionSerializer(reactions, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def reactToPost(request):
    if request.method == 'POST':
        data = request.data
        reaction_type = data['reaction']
        user_id = data['userId']
        post_id = data['postId']
        print(post_id,"post Id")
        print(user_id,"user Id")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            reaction = Reaction.objects.get(user_id=user_id, post_id=post_id)
            current_reaction = reaction.reaction
            reaction.delete()
            if reaction_type == 'like' and current_reaction == 'like':
                post.likes_count = max(0, post.likes_count - 1)

            if reaction_type == 'dislike' and current_reaction == 'dislike':
                post.dislikes_count = max(0, post.dislikes_count - 1)
            post.save()
            reaction_serializer = PostReactionSerializer(reaction, data=data, partial=True)
            if reaction_serializer.is_valid():
                return Response(reaction_serializer.data, status=status.HTTP_200_OK)
        except Reaction.DoesNotExist:
            # Creating a new reaction
            reaction = Reaction(user_id=user_id, post=post, reaction=reaction_type)
            if reaction_type == 'like':
                post.likes_count += 1
            elif reaction_type == 'dislike':
                post.dislikes_count += 1
            elif reaction_type == 'report':
                post.reports_count += 1
            post.save()

        reaction_serializer = PostReactionSerializer(reaction, data=data, partial=True)
        if reaction_serializer.is_valid():
            reaction_serializer.save()
            return Response(reaction_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(reaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def savePost(request):
    if request.method == 'POST':
        data = request.data
        user_id = data.get('userId')
        print(user_id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def listUsers(request):
    try:
        userType = request.data.get('userType')
        if userType:
            users = User.objects.filter(role=userType)
        else:
            users = User.objects.all()
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except KeyError:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
            
@api_view(['POST'])
def followUser(request):
    data = request.data
    follower_id = data.get('follower')
    following_id = data.get('following')
    
    if not follower_id or not following_id:
        return Response({'error': 'Follower and following IDs are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        follower_user = User.objects.get(id=follower_id)
    except User.DoesNotExist:
        return Response({'error': 'Follower not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        following_user = User.objects.get(id=following_id)
    except User.DoesNotExist:
        return Response({'error': 'Following User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the follower is already following the user
    follow_entry = Follow.objects.filter(follower=follower_user, following=following_user).first()
    
    if follow_entry:
        # If already following, delete the entry
        follow_entry.delete()
        return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)
    else:
        # If not following, create a new follow entry
        follow_data = {'follower': follower_user.id, 'following': following_user.id}
        serializer = FollowUsersSerializer(data=follow_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def listFollowingUsers(request):
    data = request.data
    current_user_id = data.get('currentUserId')
    
    if not current_user_id:
        return Response({'error': 'Current User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        current_user = User.objects.get(id=current_user_id)
    except User.DoesNotExist:
        return Response({'error': 'Current User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve the User instances that the current user is following
    following_users = User.objects.filter(followers__follower=current_user)
    serializer = UserSerializer(following_users, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
        

@api_view(['POST'])
def listUnfollowedUsers(request):
    data = request.data
    current_user_id = data.get('currentUserId')
    
    if not current_user_id:
        return Response({'error': 'Current User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        current_user = User.objects.get(id=current_user_id)
    except User.DoesNotExist:
        return Response({'error': 'Current User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve the users that the current user is following
    following_users = User.objects.filter(followers__follower=current_user)
    
    # Retrieve all users excluding the ones that the current user is following
    unfollowed_users = User.objects.exclude(id__in=following_users.values_list('id', flat=True)).exclude(id=current_user_id)
    serializer = UserSerializer(unfollowed_users, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


def profile(request):
    return render(request, 'profile.html')


@api_view(['POST'])
def userDetails(request):
    data = request.data
    user_id = data.get('userId')
    
    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get user details
    user_serializer = UserSerializer(user)

    # Get user's posts
    user_posts = Post.objects.filter(user=user)
    posts_serializer = PostSerializer(user_posts, many=True)

    # Get number of followers
    followers_count = Follow.objects.filter(following=user).count()

    # Get number of following
    following_count = Follow.objects.filter(follower=user).count()

    response_data = {
        'user': user_serializer.data,
        'posts': posts_serializer.data,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def send_message(request):
    sender_id = request.data.get('sender_id')
    recipient_id = request.data.get('recipient_id')
    message_text = request.data.get('message')

    try:
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    message = Message(sender=sender, recipient=recipient, message=message_text)
    message.save()
    return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_messages(request, user_id, recipient_id):
    try:
        user = User.objects.get(id=user_id)
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    messages = Message.objects.filter(
        (Q(sender_id=user_id) & Q(recipient_id=recipient_id)) |
        (Q(sender_id=recipient_id) & Q(recipient_id=user_id))
    ).order_by('timestamp')
    
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def chat(request):
    return render(request, 'chat.html')

@api_view(['POST'])
def getAllStudents(request):
    students = Student.objects.filter(role = "STUDENT")
    serializer = UserSerializer(students, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def postComment(request):
    data = request.data
    user_id = data.get('userId')
    post_id = data.get('postId')
    comment_text = data.get('comment')

    try:
        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    comment = Comments(user=user, post=post, comment=comment_text)
    comment.save()
    return Response({'message': 'Comment posted successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def getComments(request, post_id):
    comments = Comments.objects.filter(post=post_id)
    serializer = CommentsSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)