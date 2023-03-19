import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core import serializers

from base.forms import PostForm
from base.models import Comment, Follower, Post, Saved, UserProfile, Reply, Hashtag

from base.common import created_dict # a file with functions for executing required tasks


@login_required(login_url='/')
def userProfile(request, user):
    user = User.objects.get(username=user)

    # userprofile
    user_profile = UserProfile.objects.get(user=user)

    form = PostForm()

    # current user's posts
    posts = Post.objects.filter(user=user)
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

    for post in posts:
        posts_data[str(post.id)] = {}
        posts_data[str(post.id)]['total_likes'] = str(post.total_likes)
        posts_data[str(post.id)]['users_likes'] = list(post.users_likes)
        posts_data[str(post.id)]['created'] = post_created_dict[post.id]
        posts_data[str(post.id)]['saved_posts'] = list(saved_posts.filter(post=post))

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

    # hashtags and hasрtags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in hashtags:
        hashtags_dict[tag.name] = tag.hashtag_posts.count()

    # hashtags in posts json
    hashtags_json = []
    for post in posts:
        hd = {}
        hd[str(post.id)] = []
        for tag in post.hashtag.all():
            hd[str(post.id)].append(str(tag))

        hashtags_json.append(hd)

    # make a follow button
    follow_btn = "Unfollow"
    try:
        new_follower = Follower.objects.get(user=request.user, follower=user)
        follow_btn = "Unfollow"
    except:
        follow_btn = "Follow"

    # a count of follows
    posts_amount = Post.objects.filter(user=user).count() # count of user's posts
    my_following_count = Follower.objects.filter(user=request.user).count()
    other_user_following_count = Follower.objects.filter(user=user).count()
    my_followers_count = Follower.objects.filter(follower=request.user).count()
    other_user_followers_count = Follower.objects.filter(follower=user).count()

    # get the lists of my followers and following
    my_followers_ids = Follower.objects.filter(follower=request.user).values_list('user', flat=True)
    my_followers = User.objects.filter(id__in=my_followers_ids).all()
    my_following_ids = Follower.objects.filter(user=request.user).values_list('follower', flat=True)
    my_following = User.objects.filter(id__in=my_following_ids).all()
    
    # get the list of other user followers and following
    other_user_followers_ids = Follower.objects.filter(follower=user).values_list('user', flat=True)
    other_user_followers = User.objects.filter(id__in=other_user_followers_ids).all()
    other_user_following_ids = Follower.objects.filter(user=user).values_list('follower', flat=True)
    other_user_following = User.objects.filter(id__in=other_user_following_ids).all()

    # likes json with all required data (list of dicts with users that liked post)
    likes_json = []
    for post in posts:
        like_user_dict = {}
        for user_id in post.users_likes:
            like_user = User.objects.get(id=user_id)
            like_user_dict['post_id'] = str(post.id)
            like_user_dict['id'] = str(like_user.id)
            like_user_dict['username'] = like_user.username
            like_user_dict['logo'] = str(UserProfile.objects.get(user=like_user).logo)
            likes_json.append(like_user_dict.copy())
            like_user_dict.clear()

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
            # get data from post comments dropdown comment form
            if request.POST.get('post-id') != None:
                post_id = request.POST.get('post-id')
                comment_text = request.POST.get('comment-text')
                check_com_rep = comment_text[0] # check is this a comment or reply
            # get data from post comment form
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
                # comment.logo = user_profile.logo
                comment.body = request.POST.get('comment-text')
                comment.save()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # add and delete followers
        elif 'follow-unfollow-following-form' in request.POST:
            print('hello')
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
        'user': user,
        'posts': posts,
        'form': form,
        'posts_amount': posts_amount,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
        'posts_data': posts_data,
        'comments_json': comments_json,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
        'reply_created_dict': reply_created_dict,
        'follow_btn': follow_btn,
        'my_following_count': my_following_count,
        'other_user_following_count': other_user_following_count,
        'my_followers_count': my_followers_count,
        'other_user_followers_count': other_user_followers_count,
        'my_following': my_following,
        'my_followers': my_followers,
        'other_user_followers': other_user_followers,
        'other_user_following': other_user_following,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        # 'replies_dict': replies_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
        'likes_json': likes_json,
        'hashtags_json': hashtags_json,
    }

    return render(request, 'account/user_profile.html', context)


@login_required(login_url='/')
def userProfileSaved(request, user):
    # posts = Post.objects.all()
    user = User.objects.get(username=user)

    # userprofile ofa  user
    user_profile = UserProfile.objects.get(user=user)


    form = PostForm()

    # current user's posts
    posts = Post.objects.filter(saved__user=request.user)
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
    for post in posts:
        posts_data[str(post.id)] = {}
        posts_data[str(post.id)]['total_likes'] = str(post.total_likes)
        posts_data[str(post.id)]['users_likes'] = list(post.users_likes)
        posts_data[str(post.id)]['created'] = post_created_dict[post.id]
        posts_data[str(post.id)]['saved_posts'] = list(saved_posts.filter(post=post))

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
    for post in posts:
        hd = {}
        hd[str(post.id)] = []
        for tag in post.hashtag.all():
            hd[str(post.id)].append(str(tag))

        hashtags_json.append(hd)

    # creating dict; key - commentd_id, value - replies on this comment
    replies_dict = {}
    for comment in comments:
        replies_dict[comment.id] = Reply.objects.filter(comment=comment)

    # a count of follows
    posts_amount = Post.objects.filter(user=request.user).count() # count of user's posts
    my_following_count = Follower.objects.filter(user=request.user).count()
    my_followers_count = Follower.objects.filter(follower=request.user).count()

    # get the lists of my followers and following
    my_followers_ids = Follower.objects.filter(follower=request.user).values_list('user', flat=True)
    my_followers = User.objects.filter(id__in=my_followers_ids).all()
    my_following_ids = Follower.objects.filter(user=request.user).values_list('follower', flat=True)
    my_following = User.objects.filter(id__in=my_following_ids).all()

    # likes json with all required data (list of dicts with users that liked post)
    likes_json = []
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

    # get a creation date in required format; func created_dict is imported from common.py
    post_created_dict = created_dict(posts) # post creation date
    comment_created_dict = created_dict(comments) # comments creation date
    reply_created_dict = created_dict(replies) # replies creation date

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
            # get data from post comments dropdown comment form
            if request.POST.get('post-id') != None:
                post_id = request.POST.get('post-id')
                comment_text = request.POST.get('comment-text')
                check_com_rep = comment_text[0] # check is this a comment or reply
            # get data from post comment form
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
                # comment.logo = user_profile.logo
                comment.body = request.POST.get('comment-text')
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
        'form': form,
        'user_profile': user_profile,
        'posts_amount': posts_amount,
        'posts': posts,
        'saved_posts': saved_posts,
        'posts_data': posts_data,
        'comments_json': comments_json,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
        'reply_created_dict': reply_created_dict,
        'my_following_count': my_following_count,
        'my_followers_count': my_followers_count,
        'my_following': my_following,
        'my_followers': my_followers,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        'replies_dict': replies_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
        'likes_json': likes_json,
        'hashtags_json': hashtags_json,
    }
    
    return render(request, 'account/user_profile_saved.html', context)


@login_required(login_url='/')
def accountsEdit(request):
    # search
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if q != '':
        return HttpResponseRedirect(f'/?q={q}')

    form = PostForm()

    user_profile = UserProfile.objects.get(user=request.user)

    # get the list of my followers and following
    my_followers_ids = Follower.objects.filter(follower=request.user).values_list('user', flat=True)
    my_followers = User.objects.filter(id__in=my_followers_ids).all()
    my_following_ids = Follower.objects.filter(user=request.user).values_list('follower', flat=True)
    my_following = User.objects.filter(id__in=my_following_ids).all()

    # notifictions followers created
    notifications_followers_created_dict = {}
    my_followers_created = []
    my_followers_created_date = Follower.objects.filter(follower=request.user).values_list('created', flat=True)
    for i in my_followers_created_date:
        my_followers_created.append(i.strftime("%d/%m/%y %I:%M"))
    i = 0
    for follower in my_followers:
        notifications_followers_created_dict[follower] = my_followers_created[i]
        i += 1

    # hashtags and hasрtags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in hashtags:
        hashtags_dict[tag.name] = tag.hashtag_posts.count()

    # post request for creating post
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

        # account edit
        elif 'profile-edit-form' in request.POST:
            user = User.objects.get(username=request.user)
            obj = UserProfile.objects.get(user=request.user)

            user.username = request.POST.get('username')

            if request.FILES.get('new-logo') != None:
                if obj.logo != 'media/logo/empty_photo.png':
                    obj.logo.delete()
                obj.logo = request.FILES.get('new-logo')
            obj.full_name = request.POST.get('fullname')
            obj.website = request.POST.get('website')
            obj.bio = request.POST.get('bio')
            obj.email = request.POST.get('email')
            obj.phone = request.POST.get('phone')
            obj.gender = request.POST.get('gender')

            # similar account suggestions
            if request.POST.get('similar-account-suggestions') == 'check':
                obj.similar_account_suggestions = True
            elif request.POST.get('similar-account-suggestions') == None:
                obj.similar_account_suggestions = False

            if " " not in request.POST.get('username'):
                user.save()
                obj.save()
            else:
                messages.error(request, 'Usernames can only use letters, numbers, underscores and periods.')

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    context = {
        'user_profile': user_profile,
        'form': form,
        'my_followers': my_followers,
        'my_following': my_following,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
    }

    return render(request, 'account/accounts_edit.html', context)


@login_required(login_url='/')
def accountsPasswordChange(request):
    # search
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if q != '':
        return HttpResponseRedirect(f'/?q={q}')

    form = PostForm()

    user_profile = UserProfile.objects.get(user=request.user)

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

    current_password = request.POST.get('current-password')
    new_password = request.POST.get('new-password')
    confirm_new_password = request.POST.get('confirm-new-password')

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
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                # obj.logo = user_profile.logo
                obj.user = request.user
                
                # saving a post text
                post_text_value = obj.post_text
                # check is there a text or only hashtags
                if post_text_value:
                    if post_text_value[0] != "#":
                        obj.post_text = post_text_value.split("#")[0].strip()
                    else:
                        obj.post_text = ""

                obj.save()

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
                                obj.hashtag.add(hashtag)
                            except:
                                pass
                
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

        # password change
        elif 'password-change-form' in request.POST:
            check_current_password = user.check_password(current_password)
            if check_current_password and new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password was successfully updated!')
            else:
                messages.error(request, 'Your old password was entered incorrectly. Please enter it again.')


    context = {
        'user_profile': user_profile,
        'form': form,
        'my_followers': my_followers,
        'my_following': my_following,
        'notifications_followers_created_dict': notifications_followers_created_dict,
    }
    
    return render(request, 'account/accounts_password_change.html', context)


# ACTION FUNCTIONS

def removeLogo(request):
    obj = UserProfile.objects.get(user=request.user)
    if obj.logo != "media/logo/empty_photo.png":
        obj.logo.delete()
    obj.logo = "media/logo/empty_photo.png"
    obj.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
