from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register

from apps.base.models import Post, UserProfile, Follower, Hashtag
from apps.base.forms import PostForm

from .models import Chat


@login_required(login_url='/')
def inboxPage(request):
    # post form
    form = PostForm()

    users = User.objects.all()
    # user_profiles = UserProfile.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)

    # hashtags and hasрtags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in Hashtag.objects.all():
        hashtags_dict[tag.name] = tag.hashtag_posts.count()

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

    # get list of users i have chat with
    chats_check_user2 = Chat.objects.filter(user=request.user).values_list('user2', flat=True)
    chats_check_user = Chat.objects.filter(user2=request.user).values_list('user', flat=True)
    chats_check_users = list(set(list(chats_check_user2) + list(chats_check_user)))
    chats_users = User.objects.filter(id__in=chats_check_users)

    # get last message of each user
    last_message_dict = {}

    for chat_user in chats_users:
        chats_check_current_user = Chat.objects.filter(user=request.user).filter(user2=chat_user.id)
        chats_check_chat_user = Chat.objects.filter(user=chat_user.id).filter(user2=request.user)
        chats = chats_check_current_user | chats_check_chat_user
        if chats:
            last_message = chats.latest('created')
            last_message_dict[chat_user.id] = last_message
        else:
            last_message_dict[chat_user.id] = ""

    # post requests
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
        'user_profile': user_profile,
        'users': users,
        'form': form,
        'chats_users': chats_users,
        'last_message_dict': last_message_dict,
        'my_followers': my_followers,
        'my_following': my_following,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
    }
    
    return render(request, 'direct/inbox.html', context)


@login_required(login_url='/')
def openChat(request, chat_user):
    # post form
    form = PostForm()
    
    users = User.objects.all()
    
    user_profile = UserProfile.objects.get(user=request.user)

    # a user i have chat with
    chat_user = User.objects.get(username=chat_user)

    # hashtags and hasрtags count
    hashtags = Hashtag.objects.all()

    hashtags_dict = {}
    for tag in Hashtag.objects.all():
        hashtags_dict[tag.name] = tag.hashtag_posts.count()


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

    # get list of users i have chat with
    chats_check_user2 = Chat.objects.filter(user=request.user).values_list('user2', flat=True)
    chats_check_user = Chat.objects.filter(user2=request.user).values_list('user', flat=True)
    chats_check_users = list(set(list(chats_check_user2) + list(chats_check_user)))
    chats_users = User.objects.filter(id__in=chats_check_users)


    # get last message of each user
    last_message_dict = {}

    for chat_user_m in chats_users:
        chats_check_current_user = Chat.objects.filter(user=request.user).filter(user2=chat_user_m.id)
        chats_check_chat_user = Chat.objects.filter(user=chat_user_m.id).filter(user2=request.user)
        chats = chats_check_current_user | chats_check_chat_user
        if chats:
            last_message = chats.latest('created')
            last_message_dict[chat_user_m.id] = last_message
        else:
            last_message_dict[chat_user_m.id] = ""

    # post requests
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
        'users': users,
        'user_profile': user_profile,
        'form': form,
        'chats_users': chats_users,
        'chat_user': chat_user,
        'last_message_dict': last_message_dict,
        'my_followers': my_followers,
        'my_following': my_following,
        'notifications_followers_created_dict': notifications_followers_created_dict,
        'hashtags': hashtags,
        'hashtags_dict': hashtags_dict,
    }

    return render(request, 'direct/open_chat.html', context)




# get values from dictionary in templates
@register.filter
def get_item(dictionary, key):
    if dictionary is not None:
        return dictionary.get(key)