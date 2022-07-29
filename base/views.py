from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.urls import reverse

from .models import Post, UserProfile, Comment, Saved
from .forms import PostForm


def mainPage(request):
    page = 'login'
    posts = Post.objects.all()
    form = PostForm()
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user

    if len(user_profiles) > 0:  # it needs this codition, because if user is logout it will be error "matching query does not exist"
        for i in user_profiles:
            if i.user_id == request.user.id:
                user_profile = i

    # saved posts
    saved_posts = []
    try:
        saved = Saved.objects.all()
        for save in saved:
            if save.user == request.user:
                saved_posts.append(save.post_id)
    except:
        pass

    if request.method == 'POST':
        # post request for login
        if 'login-form' in request.POST:
            username = request.POST.get('username').lower()
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            else:
                messages.error(request, 'Username or password does not exist')

        # post request for creating post
        elif 'posts-tape-form' in request.POST:
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
            post_id = request.POST.get('post-id')
            comment_text = request.POST.get('comment-text')
            post_obj = Post.objects.get(id=post_id)
            comment = Comment()

            comment.post = post_obj
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = comment_text
            comment.save()


    context = {
        'page': page,
        'posts': posts,
        'form': form,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
    }
    return render(request, 'base/main_page.html', context)


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        if 'register-form' in request.POST:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                login(request, user)
            return redirect('main_page')

    context = {'form': form}
    return render(request, 'base/main_page.html', context)


def logoutUser(request):
    logout(request)
    return redirect('main_page')


def deletePost(request, pk):
    obj = Post.objects.get(id=pk)
    obj.delete()                    # deleting an image instance from database
    obj.image.delete(save=False)    # deleting an image from s3

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def postAction(request, pk):
    post = get_object_or_404(Post, id=pk)
    action = request.POST.get('actionbtn')

    if action == "like":
        # objects = post.likes.all()
        # if request.user in objects:
        #     # obj.clear()    #! delete all instances from intermidiate table many to many relationship
        # else:
        #     post.likes.add(request.user)
        post.likes.add(request.user)
            
    elif action == "save":
        saved = Saved()
        try:
            obj = Saved.objects.get(post_id=pk)
            obj.delete()
        except:
            saved.post = post
            saved.user = request.user
            saved.save()

    # return HttpResponseRedirect(reverse('main_page'))
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    comment.delete()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def userProfile(request, user):
    posts = Post.objects.all()
    form = PostForm()

    my_posts = []   # number of user's posts
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user; its equal to None when user is logout

    # it needs this codition, because if user is logout it will be error "matching query does not exist"
    if len(user_profiles) > 0:
        for i in user_profiles:
            if i.user.id == request.user.id:
                user_profile = i

    # a cycle for counting a number of user's posts
    for post in posts:
        if post.user == request.user:
            my_posts.append(post)
    my_posts_amount = len(my_posts) # amount of user's posts

    # saved posts
    saved_posts = []
    try:
        saved = Saved.objects.all()
        for save in saved:
            if save.user == request.user:
                saved_posts.append(save.post_id)
    except:
        pass

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
            post_id = request.POST.get('post-id')
            comment_text = request.POST.get('comment-text')
            post_obj = Post.objects.get(id=post_id)
            comment = Comment()

            comment.post = post_obj
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = comment_text
            comment.save()

    context = {
        'posts': posts,
        'form': form,
        'my_posts_amount': my_posts_amount,
        'user_profile': user_profile,
        'saved_posts': saved_posts,
    }
    return render(request, 'account/user_profile.html', context)


def userProfileSaved(request, user):
    posts = Post.objects.all()
    saved = Saved.objects.all()
    form = PostForm()

    saved_posts = [] # an amount of saved posts
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user

    if len(user_profiles) > 0:  # it needs this codition, because if user is logout it will be error "matching query does not exist"
        for i in user_profiles:
            if i.user.id == request.user.id:
                user_profile = i

    # a cycle for counting a number of user's posts
    for save in saved:
        if save.user == request.user:
            saved_posts.append(save)
    saved_posts_amount = len(saved_posts) # amount of user's posts

    # saved posts
    saved_posts = []
    try:
        saved = Saved.objects.all()
        for save in saved:
            if save.user == request.user:
                saved_posts.append(save.post_id)
    except:
        pass

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
            post_id = request.POST.get('post-id')
            comment_text = request.POST.get('comment-text')
            post_obj = Post.objects.get(id=post_id)
            comment = Comment()

            comment.post = post_obj
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = comment_text
            comment.save()

    context = {
        'posts': posts,
        'form': form,
        'user_profile': user_profile,
        'saved_posts_amount': saved_posts_amount,
        'saved_posts': saved_posts,
    }
    
    return render(request, 'account/user_profile_saved.html', context)


def userProfileTagged(request, user):
    posts = Post.objects.all()
    form = PostForm()

    my_posts = []   # number of user's posts
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user

    if len(user_profiles) > 0:  # it needs this codition, because if user is logout it will be error "matching query does not exist"
        for i in user_profiles:
            if i.django_user_model_id == request.user.id:
                user_profile = i

        # a cycle for counting a number of user's posts
    for post in posts:
        if post.user == request.user:
            my_posts.append(post)
    my_posts_amount = len(my_posts) # amount of user's posts

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

        # post request for adding a comments
        elif 'add-comment-form' in request.POST:
            post_id = request.POST.get('post-id')
            comment_text = request.POST.get('comment-text')
            post_obj = Post.objects.get(id=post_id)
            comment = Comment()

            comment.post = post_obj
            comment.user = request.user
            comment.logo = user_profile.logo
            comment.body = comment_text
            comment.save()

    context = {
        'posts': posts,
        'form': form,
        'my_posts_amount': my_posts_amount,
        'user_profile': user_profile,
    }
    return render(request, 'account/user_profile_tagged.html', context)

# ACCOUNT SETTINGS
def accountsEdit(request):
    form = PostForm()
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user

    if len(user_profiles) > 0:  # it needs this codition, because if user is logout it will be error "matching query does not exist"
        for i in user_profiles:
            if i.user_id == request.user.id:
                user_profile = i

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

            obj.full_name = request.POST.get('fullname')
            user.username = request.POST.get('username')
            obj.website = request.POST.get('website')
            obj.bio = request.POST.get('bio')
            obj.email = request.POST.get('email')
            obj.phone = request.POST.get('phone')
            obj.gender = request.POST.get('gender')
            
            user.save()
            obj.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    context = {
        'user_profile': user_profile,
        'form': form,
    }

    return render(request, 'account_settings/accounts_edit.html', context)


def accountsPasswordChange(request):
    form = PostForm()
    user_profiles = UserProfile.objects.all()
    user_profile = None         # user profile (logo) of a current user

    if len(user_profiles) > 0:  # it needs this codition, because if user is logout it will be error "matching query does not exist"
        for i in user_profiles:
            if i.django_user_model_id == request.user.id:
                user_profile = i

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

    context = {
        'user_profile': user_profile,
        'form': form,
    }
    
    return render(request, 'account_settings/accounts_password_change.html', context)