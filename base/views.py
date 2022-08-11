from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.urls import reverse
from django.utils import timezone
from django.template.defaulttags import register

from .models import Post, UserProfile, Comment, Saved
from .forms import PostForm, UserProfileForm, RegistrationForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def mainPage(request):
    page = 'login'
    posts = Post.objects.all()
    comments = Comment.objects.all()
    form = PostForm()

    # if it wasn't here try/except it will be error when user is logout
    saved_posts = None
    try:
        saved_posts = Saved.objects.filter(user=request.user).values_list('post', flat=True) # returns a list of post ids of saved objs
    except:
        pass

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

    # post created date
    post_created_dict = {}

    for post_c in posts:
        post_created = post_c.created
        now = timezone.now()
        period = now - post_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            post_created_dict[post_c.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                post_created_dict[post_c.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    post_created_dict[post_c.id] = min
                else:
                    sec = str(sec_int) + "s"
                    post_created_dict[post_c.id] = sec

    # comments crated date
    comment_created_dict = {}

    for comment in comments:
        comment_created = comment.created
        now = timezone.now()
        period = now - comment_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            comment_created_dict[comment.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                comment_created_dict[comment.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    comment_created_dict[comment.id] = min
                else:
                    sec = str(sec_int) + "s"
                    comment_created_dict[comment.id] = sec

    if request.method == 'POST':
        # post request for login
        if 'login-form' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                messages.error(request, 'Sorry, your password was incorrect. Please double-check your password.')

        # post request for creating post
        elif 'post-create-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post request for editing post
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text
            obj.save()

        # post request for adding a comments
        elif 'add-comment-form' in request.POST:
            comment = Comment()
            post_id = request.POST.get('post-id')

            comment.post = Post.objects.get(id=post_id)
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = request.POST.get('comment-text')
            comment.save()

    context = {
        'page': page,
        'posts': posts,
        'form': form,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
    }
    
    return render(request, 'base/main_page.html', context)


def registerPage(request):
    user_create_form = RegistrationForm()

    user_profiles = UserProfile.objects.all()

    if request.method == 'POST':
        if 'register-form' in request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()

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


def logoutUser(request):
    logout(request)
    return redirect('main_page')


def deletePost(request, pk):
    obj = Post.objects.get(id=pk)
    obj.delete()                    # deleting a post
    obj.image.delete(save=False)    # deleting an image from s3

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def postAction(request, pk):
    # post = get_object_or_404(Post, id=pk)
    post = Post.objects.get(id=pk)
    action = request.POST.get('actionbtn')

    if action == "like":
        # objects = post.likes.all()
        # if request.user in objects:
        #     # obj.clear()    #! delete all instances from intermidiate table many to many relationship
        # else:
        #     post.likes.add(request.user)
        post.likes.add(request.user)
            
    elif action == "save":
        # add like on post or delete if it already exist
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


def userProfile(request, user):
    user = User.objects.get(username=user)
    posts = Post.objects.all()
    comments = Comment.objects.all()
    form = PostForm()
    saved_posts = Saved.objects.filter(user=request.user).values_list('post', flat=True) # returns a list of post_id in saved

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=user)
    except:
        pass

    my_posts_amount = Post.objects.filter(user=user).count() # count of user's posts

    # post created date
    post_created_dict = {}

    for post_c in posts:
        post_created = post_c.created
        now = timezone.now()
        period = now - post_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            post_created_dict[post_c.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                post_created_dict[post_c.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    post_created_dict[post_c.id] = min
                else:
                    sec = str(sec_int) + "s"
                    post_created_dict[post_c.id] = sec

    # comments crated date
    comment_created_dict = {}

    for comment in comments:
        comment_created = comment.created
        now = timezone.now()
        period = now - comment_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            comment_created_dict[comment.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                comment_created_dict[comment.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    comment_created_dict[comment.id] = min
                else:
                    sec = str(sec_int) + "s"
                    comment_created_dict[comment.id] = sec

    if request.method == 'POST':
        # post request for creating post
        if 'posts-tape-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post request for editing post
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text
            obj.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post request for adding a comments
        elif 'add-comment-form' in request.POST:
            comment = Comment()
            post_id = request.POST.get('post-id')

            comment.post = Post.objects.get(id=post_id)
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = request.POST.get('comment-text')
            comment.save()

    context = {
        'user': user,
        'posts': posts,
        'form': form,
        'my_posts_amount': my_posts_amount,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
    }
    return render(request, 'account/user_profile.html', context)


def userProfileSaved(request, user):
    posts = Post.objects.all()
    comments = Comment.objects.all()
    form = PostForm()

    # saved = Saved.objects.filter(user=request.user)
    saved_objs = Post.objects.filter(saved__user=request.user)
    saved_posts = Saved.objects.filter(user=request.user).values_list('post', flat=True) # for changing a save button
    my_posts_amount = Post.objects.filter(user=request.user).count() # count of user's posts

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

    # post created date
    post_created_dict = {}

    for post_c in posts:
        post_created = post_c.created
        now = timezone.now()
        period = now - post_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            post_created_dict[post_c.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                post_created_dict[post_c.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    post_created_dict[post_c.id] = min
                else:
                    sec = str(sec_int) + "s"
                    post_created_dict[post_c.id] = sec

    # comments crated date
    comment_created_dict = {}

    for comment in comments:
        comment_created = comment.created
        now = timezone.now()
        period = now - comment_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            comment_created_dict[comment.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                comment_created_dict[comment.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    comment_created_dict[comment.id] = min
                else:
                    sec = str(sec_int) + "s"
                    comment_created_dict[comment.id] = sec

    if request.method == 'POST':
        # post request for creating post
        if 'posts-tape-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post request for editing post
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text
            obj.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # post request for adding a comments
        elif 'add-comment-form' in request.POST:
            comment = Comment()
            post_id = request.POST.get('post-id')

            comment.post = Post.objects.get(id=post_id)
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = request.POST.get('comment-text')
            comment.save()

    context = {
        'form': form,
        'user_profile': user_profile,
        'my_posts_amount': my_posts_amount,
        'saved_objs': saved_objs,
        'saved_posts': saved_posts,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
    }
    
    return render(request, 'account/user_profile_saved.html', context)
    

def removeLogo(request):
    obj = UserProfile.objects.get(user=request.user)
    if obj.logo != "media/logo/empty_photo.png":
        obj.logo.delete()
    obj.logo = "media/logo/empty_photo.png"
    obj.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


# ACCOUNT SETTINGS
def accountsEdit(request):
    form = PostForm()
    user_profile_form = UserProfileForm()

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

    # post request for creating post
    if request.method == 'POST':
        if 'posts-tape-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

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
            
            # saving gender value
            user_profile_form = UserProfileForm(request.POST, instance=obj)
            if user_profile_form.is_valid():
                user_profile_form.save()

            # similar account suggestions
            if request.POST.get('similar-account-suggestions') == 'check':
                obj.similar_account_suggestions = True
            elif request.POST.get('similar-account-suggestions') == None:
                obj.similar_account_suggestions = False

            user.save()
            obj.save()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    context = {
        'user_profile': user_profile,
        'form': form,
        'user_profile_form': user_profile_form,
    }

    return render(request, 'account_settings/accounts_edit.html', context)


def accountsPasswordChange(request):
    form = PostForm()
    user = User.objects.get(username=request.user)

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

    current_password = request.POST.get('current-password')
    new_password = request.POST.get('new-password')
    confirm_new_password = request.POST.get('confirm-new-password')

    # post request for creating post
    if request.method == 'POST':
        if 'post-create-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

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
    }
    
    return render(request, 'account_settings/accounts_password_change.html', context)


def explorePage(request):
    posts = Post.objects.all()
    comments = Comment.objects.all()
    form = PostForm()

    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        pass

# post created date
    post_created_dict = {}

    for post_c in posts:
        post_created = post_c.created
        now = timezone.now()
        period = now - post_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            post_created_dict[post_c.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                post_created_dict[post_c.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    post_created_dict[post_c.id] = min
                else:
                    sec = str(sec_int) + "s"
                    post_created_dict[post_c.id] = sec

    # comments crated date
    comment_created_dict = {}

    for comment in comments:
        comment_created = comment.created
        now = timezone.now()
        period = now - comment_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if day_int > 0:
            day = str(day_int) + "d"
            comment_created_dict[comment.id] = day
        else:
            if hour_int > 0:
                hour = str(hour_int) + "h"
                comment_created_dict[comment.id] = hour
            else:
                if min_int > 0:
                    min = str(min_int) + "m"
                    comment_created_dict[comment.id] = min
                else:
                    sec = str(sec_int) + "s"
                    comment_created_dict[comment.id] = sec

    # post request for creating post
    if request.method == 'POST':
        if 'post-create-form' in request.POST:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.logo = user_profile.logo
                obj.user = request.user
                obj.save()
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
                
        # post request for editing post
        elif 'post-edit-form' in request.POST:
            post_id = request.POST.get('post-id')
            post_text = request.POST.get('post-text')
            obj = Post.objects.get(id=post_id)
            obj.post_text = post_text
            obj.save()

        # post request for adding a comments
        elif 'add-comment-form' in request.POST:
            comment = Comment()
            post_id = request.POST.get('post-id')

            comment.post = Post.objects.get(id=post_id)
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = request.POST.get('comment-text')
            comment.save()

    context = {
        'posts': posts,
        'form': form,
        'post_created_dict': post_created_dict,
        'comment_created_dict': comment_created_dict,
    }
    
    return render(request, 'base/explore.html', context)