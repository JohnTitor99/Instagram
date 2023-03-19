from datetime import datetime
from itertools import chain
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core import serializers

from .forms import PostForm, RegistrationForm
from .models import Comment, Follower, Post, Saved, UserProfile, Reply, Hashtag

from .common import created_dict # a file with functions for executing required tasks


def mainPage(request):
    # validation on login user for displaying login or register page
    page = 'login'

    # post form
    post_form = PostForm()

    # userprofile of a current user
    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

    posts = None
    saved_posts = None
    comments = None
    replies = None
    try:
        # get my and my followers posts
        following_users = Follower.objects.filter(user=request.user).values('follower') # get a query set of follower field
        other_users_posts = Post.objects.filter(user__in=following_users).all() # filter with multiple values
        my_posts = Post.objects.filter(user=request.user)
        posts = other_users_posts | my_posts

        # saved posts
        saved_posts = Saved.objects.filter(user=request.user).values_list('post', flat=True) # returns a list of post ids of saved objs

        # comments
        comments = Comment.objects.filter(post__in=posts)

        # replies
        replies = Reply.objects.filter(comment__in=comments)
    except:
        pass

    # get a creation date in required format; func created_dict is imported from common.py
    post_created_dict = created_dict(posts) if posts else None # post creation date
    comment_created_dict = created_dict(comments) if comments else None # comments creation date
    reply_created_dict = created_dict(replies) if replies else None # replies creation date

    # additional info for post comments
    posts_data = {}
    try:
        for post in posts:
            posts_data[str(post.id)] = {}
            posts_data[str(post.id)]['total_likes'] = str(post.total_likes)
            posts_data[str(post.id)]['users_likes'] = list(post.users_likes)
            posts_data[str(post.id)]['created'] = post_created_dict[post.id]
            posts_data[str(post.id)]['saved_posts'] = list(saved_posts.filter(post=post))
    except:
        pass

    # comments for post comments dropdown
    comments_json = None
    try:
        comments_str_json = serializers.serialize('json', comments)
        comments_json = json.loads(comments_str_json)
        # adding comments
        for n in comments_json:
            comments_json_user = User.objects.get(id=n['fields']['user'])
            n['adj_dict'] = {}
            n['adj_dict']['username'] = comments_json_user.username
            n['adj_dict']['logo'] = str(UserProfile.objects.get(user=comments_json_user).logo)
            n['adj_dict']['created'] = comment_created_dict[n['pk']]
            # adding replies
            n['replies'] = []
            replies_json = Reply.objects.filter(comment=Comment.objects.get(id=n['pk']))
            if replies_json:
                for i in replies_json:
                    replies_dict = {}
                    replies_dict['pk'] = i.id
                    replies_dict['user'] = i.user.id
                    replies_dict['username'] = str(User.objects.get(id=i.user.id))
                    replies_dict['related_user'] = i.related_user.id
                    replies_dict['related_username'] = str(User.objects.get(id=i.related_user.id))
                    replies_dict['logo'] = str(UserProfile.objects.get(user=User.objects.get(id=i.user.id)).logo)
                    replies_dict['body'] = i.body
                    replies_dict['created'] = reply_created_dict[i.id]
                    n['replies'].append(replies_dict)                
    except:
        pass
    
    # comments and replies count
    comments_count_dict = {}
    try:
        for post in posts:
            com_count = comments.filter(post=post).count() if comments else 0
            rep_count = replies.filter(comment__in=Comment.objects.filter(post=post)).count() if replies else 0
            com_rep_count = com_count + rep_count
            comments_count_dict[post.id] = com_rep_count
    except:
        pass

    # hashtags and hasрtags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in Hashtag.objects.all():
        hashtags_dict[tag.name] = tag.hashtag_posts.count()

    # hashtags in posts json
    hashtags_json = []
    try:
        for post in posts:
            hd = {}
            hd[str(post.id)] = []
            for tag in post.hashtag.all():
                hd[str(post.id)].append(str(tag))

            hashtags_json.append(hd)
    except:
        pass


    # users for suggestions
    suggested_users = []
    try:
        # check that user is my follower
        for s_user in Follower.objects.filter(follower=request.user).order_by('?'):
            # check that i'm not his follower
            if s_user.user.id not in Follower.objects.filter(user=request.user).values_list('follower', flat=True):
                ss_user = User.objects.get(id=s_user.user.id)
                suggested_users.append(ss_user)
    except:
        pass

    suggested_users = suggested_users[:5] # get 5 elements

    # get the lists of my followers and following
    my_followers = None
    my_following = None

    try:
        my_followers_ids = Follower.objects.filter(follower=request.user).values_list('user', flat=True)
        my_followers = User.objects.filter(id__in=my_followers_ids).all()
        my_following_ids = Follower.objects.filter(user=request.user).values_list('follower', flat=True)
        my_following = User.objects.filter(id__in=my_following_ids).all()
    except:
        pass

    # likes json with all required data (list of dicts with users that liked post)
    likes_json = []
    try:
        for post in posts:
            like_user_dict = {}
            for user_id in post.users_likes:
                user = User.objects.get(id=user_id)
                like_user_dict['post_id'] = str(post.id)
                like_user_dict['id'] = str(user.id)
                like_user_dict['username'] = user.username
                like_user_dict['logo'] = str(UserProfile.objects.get(user=user).logo)
                likes_json.append(like_user_dict.copy())
                like_user_dict.clear()
    except:
        pass

    # getting a date when user has followed me for notifications
    notifications_followers_created_dict = {}
    try:
        my_followers_created = []
        my_followers_created_date = Follower.objects.filter(follower=request.user).values_list('created', flat=True)
        for i in my_followers_created_date:
            my_followers_created.append(i.strftime("%d/%m/%y %I:%M"))
        i = 0
        for follower in my_followers:
            notifications_followers_created_dict[follower] = my_followers_created[i]
            i += 1
    except:
        pass


    

    # POST requests
    if request.method == 'POST':
        # login
        if 'login-form' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                messages.error(request, 'Sorry, your password was incorrect. Please double-check your password.')

        # create a post
        elif 'post-create-form' in request.POST:
            new_post = Post()
            new_post.user = request.user
            new_post.image = request.FILES.get('post-create-image')
            new_post.image_dimensions = request.POST.get('post-create-image-dimensions')

            # saving a post text
            post_text_value = request.POST.get('post-create-text')
            # check are there hashtags or not
            if post_text_value:
                if post_text_value[0] != "#":
                    new_post.post_text = post_text_value.split("#")[0].strip()
                else:
                    new_post.post_text = ""

            new_post.save()

            # saving post tags
            # for saving something to manytomany field you need to save the model instance before that
            post_text_value_split = post_text_value.split(" ")
            for tag in post_text_value_split:
                if tag != "":
                    tag = tag.strip()
                    if tag[0] == "#":
                        tag = tag.replace("#", "")
                        # save a hashtag if it exists
                        try:
                            hashtag = Hashtag.objects.get(name=tag)
                            new_post.hashtag.add(hashtag)
                        except:
                            pass
                
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post edit
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text.split("#")[0].strip()
            obj.image.name.replace('media/images/', '') # without this replace it will double a path to the image
            obj.save()

            post_text_value_split = post_text.split(" ")
            for tag in post_text_value_split:
                if tag != "":
                    tag = tag.strip()
                    if tag[0] == "#":
                        tag = tag.replace("#", "")
                        try:
                            hashtag = Hashtag.objects.get(name=tag)
                            obj.hashtag.add(hashtag)
                        except:
                            pass

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # add comments and replies
        elif 'add-comment-form' in request.POST:
            # get comment data from post comment form or post comments dropdown form (bcs of js)
            post_id = None
            check_com_rep = None
            if request.POST.get('post-id') != None:
                post_id = request.POST.get('post-id')
                comment_text = request.POST.get('comment-text')
                check_com_rep = comment_text[0] # check is this a comment or reply
            else:
                post_id = request.POST.get('post-post-id')
                comment_text = request.POST.get('post-comment-text')
                
            # saving reply
            if check_com_rep == "@":
                comment = Comment.objects.get(id=request.POST.get('comment-id'))

                reply_body_split = request.POST.get('comment-text').split(" ")

                related_user =  User.objects.get(username=reply_body_split[0].replace("@", "")) # get a user's name from @user comment...

                reply_body = request.POST.get('comment-text').replace(reply_body_split[0] + "", "")
                Reply.objects.create(comment=comment, user=request.user, related_user=related_user, body=reply_body)

            # saving comment
            else:
                comment = Comment()
                comment.post = Post.objects.get(id=post_id)
                comment.user = request.user
                comment.body = comment_text
                comment.save()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # add and delete followers
        elif 'follow-unfollow-following-form' in request.POST:
            following_id = request.POST.get('following')
            following = User.objects.get(id=following_id)
            check_follow = request.POST.get('check-follow')

            # follow or unfollow user
            if check_follow == "Follow":
                new_follower = Follower.objects.create(user=request.user, follower=following)
                new_follower.save()

                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                del_follower = Follower.objects.get(user=request.user, follower=following)
                del_follower.delete()

                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # delete a following user
        elif 'unfollow-follower-form' in request.POST:
            follower_id = request.POST.get('follower')
            follower = User.objects.get(id=follower_id)

            del_follower = Follower.objects.get(user=follower, follower=request.user)
            del_follower.delete()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    context = {
        'page': page,
        'posts': posts,
        'posts_data': posts_data,
        'comments_json': comments_json,
        'suggested_users': suggested_users,
        'post_form': post_form,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
        'comments_count_dict': comments_count_dict,
        'reply_created_dict': reply_created_dict,
        'my_followers': my_followers,
        'my_following': my_following,
        'likes_json': likes_json,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        'hashtags': hashtags,
        'hashtags_json': hashtags_json,
        'hashtags_dict': hashtags_dict,
    }
    
    return render(request, 'base/main_page.html', context)


def registerPage(request):
    user_create_form = RegistrationForm()

    user_profiles = UserProfile.objects.all()

    # POST requests
    if request.method == 'POST':
        # registration
        if 'register-form' in request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                # saving a user model
                user = form.save(commit=False)
                user.save()

                # saving a userprofile model
                user_p = user_profiles.create(user=user)
                phone_or_email = request.POST.get('phone-or-email')
                if '@' in phone_or_email:
                    user_p.email = phone_or_email
                else:
                    user_p.phone = phone_or_email
                user_p.full_name = request.POST.get('full-name')
                user_p.save()

                login(request, user)
                return redirect('main_page')

    context = {
        'user_create_form': user_create_form,
    }

    return render(request, 'base/main_page.html', context)


@login_required(login_url='/')
def goToPost(request, pk):
    # post form
    form = PostForm()

    # userprofile for a current user
    user_profile = UserProfile.objects.get(user=request.user)
    
    # get my and my followers posts
    post = Post.objects.get(id=pk) # go to this  post

    post_user = getattr(post, 'user') # owner of this post
    
    posts = Post.objects.filter(user=post_user)[:6] # the first 6 posts of this user

    # saved posts
    saved_posts = Saved.objects.filter(user=request.user).values_list('post', flat=True) # returns a list of post ids of saved objs

    # comments
    comments = Comment.objects.filter(post__in=posts)

    # replies
    replies = Reply.objects.filter(comment__in=comments)

    # get a creation date in required format; func created_dict is imported from common.py
    post_created_dict = created_dict(posts) if posts else None # post creation date
    comment_created_dict = created_dict(comments) if comments else None # comments creation date
    reply_created_dict = created_dict(replies) if replies else None # replies creation date

    # additional info for post comments
    posts_data = {}
    for post_data in posts:
        posts_data[str(post_data.id)] = {}
        posts_data[str(post_data.id)]['total_likes'] = str(post_data.total_likes)
        posts_data[str(post_data.id)]['users_likes'] = list(post_data.users_likes)
        posts_data[str(post_data.id)]['created'] = post_created_dict[post_data.id]
        posts_data[str(post_data.id)]['saved_posts'] = list(saved_posts.filter(post=post_data))

    # comments for post comments dropdown
    comments_str_json = serializers.serialize('json', comments)
    comments_json = json.loads(comments_str_json)
    # adding comments
    for n in comments_json:
        comments_json_user = User.objects.get(id=n['fields']['user'])
        n['adj_dict'] = {}
        n['adj_dict']['username'] = comments_json_user.username
        n['adj_dict']['logo'] = str(UserProfile.objects.get(user=comments_json_user).logo)
        n['adj_dict']['created'] = comment_created_dict[n['pk']]
        # adding replies
        n['replies'] = []
        replies_json = Reply.objects.filter(comment=Comment.objects.get(id=n['pk']))
        if replies_json:
            for i in replies_json:
                replies_dict = {}
                replies_dict['pk'] = i.id
                replies_dict['user'] = i.user.id
                replies_dict['username'] = str(User.objects.get(id=i.user.id))
                replies_dict['related_user'] = i.related_user.id
                replies_dict['related_username'] = str(User.objects.get(id=i.related_user.id))
                replies_dict['logo'] = str(UserProfile.objects.get(user=User.objects.get(id=i.user.id)).logo)
                replies_dict['body'] = i.body
                replies_dict['created'] = reply_created_dict[i.id]
                n['replies'].append(replies_dict)

    # hashtags and hastags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in Hashtag.objects.all():
        hashtags_dict[tag.name] = tag.hashtag_posts.count()

    # hashtags in posts json
    hashtags_json = []
    for post_data in posts:
        hd = {}
        hd[str(post_data.id)] = []
        for tag in post.hashtag.all():
            hd[str(post_data.id)].append(str(tag))

        hashtags_json.append(hd)

    likes_json = []
    for post_data in posts:
        like_user_dict = {}
        for user_id in post_data.users_likes:
            user = User.objects.get(id=user_id)
            like_user_dict['post_id'] = str(post_data.id)
            like_user_dict['id'] = str(user.id)
            like_user_dict['username'] = user.username
            like_user_dict['logo'] = str(UserProfile.objects.get(user=user).logo)
            likes_json.append(like_user_dict.copy())
            like_user_dict.clear()

    # get the list of my followers and following
    my_followers_ids = Follower.objects.filter(follower=request.user).values_list('user', flat=True)
    my_followers = User.objects.filter(id__in=my_followers_ids).all()
    my_following_ids = Follower.objects.filter(user=request.user).values_list('follower', flat=True)
    my_following = User.objects.filter(id__in=my_following_ids).all()

    # getting a date when user has followed me for notifications
    notifications_followers_created_dict = {}
    my_followers_created = []
    my_followers_created_date = Follower.objects.filter(follower=request.user).values_list('created', flat=True)
    for i in my_followers_created_date:
        my_followers_created.append(i.strftime("%d/%m/%y %I:%M"))
    i = 0
    for follower in my_followers:
        notifications_followers_created_dict[follower] = my_followers_created[i]
        i += 1

    # POST request
    if request.method == 'POST':
        # login
        if 'login-form' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            # check a user with this username and password exists or not
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                messages.error(request, 'Sorry, your password was incorrect. Please double-check your password.')

        # post create
        elif 'post-create-form' in request.POST:
            new_post = Post()
            new_post.user = request.user
            new_post.image = request.FILES.get('post-create-image')
            new_post.image_dimensions = request.POST.get('post-create-image-dimensions')

            # saving a post text
            post_text_value = request.POST.get('post-create-text')
            # check are there hashtags or not
            if post_text_value:
                if post_text_value[0] != "#":
                    new_post.post_text = post_text_value.split("#")[0].strip()
                else:
                    new_post.post_text = ""

            new_post.save()

            # saving post tags
            # for saving something to manytomany field you need to save the model instance before that
            post_text_value_split = post_text_value.split(" ")
            for tag in post_text_value_split:
                if tag != "":
                    tag = tag.strip()
                    if tag[0] == "#":
                        tag = tag.replace("#", "")
                        # save a hashtag if it exists
                        try:
                            hashtag = Hashtag.objects.get(name=tag)
                            new_post.hashtag.add(hashtag)
                        except:
                            pass
                
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post edit
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text.split("#")[0].strip()
            obj.image.name.replace('media/images/', '') # without this replace it will double a path to the image
            obj.save()

            post_text_value_split = post_text.split(" ")
            for tag in post_text_value_split:
                if tag != "":
                    tag = tag.strip()
                    if tag[0] == "#":
                        tag = tag.replace("#", "")
                        try:
                            hashtag = Hashtag.objects.get(name=tag)
                            obj.hashtag.add(hashtag)
                        except:
                            pass

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # add comments and replies
        elif 'add-comment-form' in request.POST:
            # get comment data from post comment form or post comments dropdown form (bcs of js)
            post_id = None
            check_com_rep = None
            if request.POST.get('post-id') != None:
                post_id = request.POST.get('post-id')
                comment_text = request.POST.get('comment-text')
                check_com_rep = comment_text[0] # check is this a comment or reply
            else:
                post_id = request.POST.get('post-post-id')
                comment_text = request.POST.get('post-comment-text')
                
            # saving reply
            if check_com_rep == "@":
                comment = Comment.objects.get(id=request.POST.get('comment-id'))

                reply_body_split = request.POST.get('comment-text').split(" ")

                related_user =  User.objects.get(username=reply_body_split[0].replace("@", "")) # get a user's name from @user comment...

                reply_body = request.POST.get('comment-text').replace(reply_body_split[0] + "", "")
                Reply.objects.create(comment=comment, user=request.user, related_user=related_user, body=reply_body)

            # saving comment
            else:
                comment = Comment()
                comment.post = Post.objects.get(id=post_id)
                comment.user = request.user
                comment.body = comment_text
                comment.save()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # add and delete followers
        elif 'follow-unfollow-following-form' in request.POST:
            following_id = request.POST.get('following')
            following = User.objects.get(id=following_id)
            check_follow = request.POST.get('check-follow')

            # follow or unfollow user
            if check_follow == "Follow":
                new_follower = Follower.objects.create(user=request.user, follower=following)
                new_follower.save()

                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                del_follower = Follower.objects.get(user=request.user, follower=following)
                del_follower.delete()

                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # delete a following user
        elif 'unfollow-follower-form' in request.POST:
            follower_id = request.POST.get('follower')
            follower = User.objects.get(id=follower_id)

            del_follower = Follower.objects.get(user=follower, follower=request.user)
            del_follower.delete()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    context = {
        'posts': posts,
        'form': form,
        'post': post,
        'posts_data': posts_data,
        'post_user': post_user,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
        'post_created_dict': post_created_dict,
        'comments_json': comments_json,
        'comment_created_dict': comment_created_dict,
        'reply_created_dict': reply_created_dict,
        'my_followers': my_followers,
        'my_following': my_following,
        'likes_json': likes_json,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        # 'replies_dict': replies_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
        'hashtags_json': hashtags_json,
    }
    
    return render(request, 'base/go_to_post.html', context)





# ACTION FUNCTIONS

# get values from dictionary in templates
@register.filter
def get_item(dictionary, key):
    if dictionary is not None:
        return dictionary.get(key)


def logoutUser(request):
    logout(request)
    return redirect('main_page')


def deletePost(request, pk):
    obj = Post.objects.get(id=pk)
    obj.delete()                    # deleting a post
    obj.image.delete(save=False)    # deleting an image from static files

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def postAction(request, pk):
    action = request.POST.get('actionbtn')
    post = Post.objects.get(id=pk)
    # add like to the post
    if action == "like":
        # m = Post.objects.create()
        post.likes.add(request.user)

    # delete like from the post
    elif action == "unlike":
        for like_user in post.likes.all():
            if like_user.id == request.user.id:
                post.likes.remove(like_user)
            
    # save the post to saved
    elif action == "save":
        saved = Saved()
        try:
            obj = Saved.objects.get(post_id=pk, user=request.user)
            if obj.user == request.user:
                obj.delete()
        except:
            saved.post = post
            saved.user = request.user
            saved.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    comment.delete()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def deleteReply(request, pk):
    reply = Reply.objects.get(id=pk)
    reply.delete()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))







