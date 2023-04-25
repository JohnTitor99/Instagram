from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth.models import User
from apps.base.models import Post, Saved, Comment, Follower
from .serializers import UserSerializer, PostSerializer, SavedPostsSerializer, CommentSerializer, FollowSerializer


@api_view(['GET'])
def apiOverview(request):
    urls = {
        'User by Name': '/user/<username>/',
        'User by Id': '/user/<user_id>/',
        'All Users': '/users/',

        'User\'s Posts': '/posts/<username>/',
        'Add Post': '/add-post/',
        'Update Post': '/update-post/<post_id>/',
        'Delete Post': '/delete-post/<post_id>/',

        'Saved Posts': '/saved-posts/<username>/',

        'Post Comments': '/comments/<post_id>/',
        'Add Comment': '/add-comment/',
        'Update Comment': '/update-comment/<comment_id>/',
        'Delete Comment': '/delete-comment/<comment_id>/',

        'User\'s Followers': '/followers/<user_id>',
        'User\'s Following': '/following/<user_id>',
    }
    return Response(urls)


# --- USER ---

@api_view(['GET'])
def getUserByName(request, username):
    user = User.objects.get(username=username)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getUserById(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# --- POSTS ---

@api_view(['GET'])
def getPosts(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addPost(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def updatePost(request, post_id):
    post = Post.objects.get(id=post_id)
    serializer = PostSerializer(instance=post, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deletePost(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return Response("Post is deleted.")



# --- SAVED POSTS ---

@api_view(['GET'])
def getSavedPosts(request, username):
    user = User.objects.get(username=username)
    saved = Saved.objects.filter(user=user).values_list('post', flat=True)
    saved_posts = Post.objects.filter(id__in=saved)
    serializer = SavedPostsSerializer(saved_posts, many=True)
    return Response(serializer.data)



# --- COMMENTS ---

@api_view(['GET'])
def getComments(request, post_id):
    comments = Comment.objects.filter(post=post_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addComment(request):
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def updateComment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    serializer = CommentSerializer(instance=comment, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteComment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return Response("Comment is deleted.")


# --- FOLLOWERS AND FOLLOWING ---

@api_view(['GET'])
def getFollowers(request, username):
    user = User.objects.get(username=username)
    followers = Follower.objects.filter(follower=user)
    serializer = FollowSerializer(followers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getFollowing(request, username):
    user = User.objects.get(username=username)
    following = Follower.objects.filter(user=user)
    serializer = FollowSerializer(following, many=True)
    return Response(serializer.data)