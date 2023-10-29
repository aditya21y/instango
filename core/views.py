from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@login_required(login_url='signin')
def index(request):
    profile = User.objects.get(username=request.user.username)
    profile_user = Profile.objects.get(user=profile)
    posts = Post.objects.all()
    return render(request,'index.html',{"profile_user":profile_user,"posts":posts})

@login_required(login_url='signin')
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user,image=image,caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')

@csrf_exempt
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id = post_id)

    like_filter = LikePost.objects.filter(post_id = post_id, username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id = post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        like = "Liked By",post.no_of_likes
        return redirect('/')
        # return HttpResponse (like)
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        like = "Liked By",post.no_of_likes
        return redirect('/')
        # return HttpResponse (like)

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')
    return render(request,'setting.html',{'user_profile':user_profile})

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email is Already Taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,"Username is Already Taken")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()

                #log in user and redirect to settings
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)

                #create profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user = user_model.id)
                new_profile.save()

                return redirect('settings')
        else:
            messages.info(request,"Password not Match")
            return redirect('signup')
    else:
        return render(request,'signup.html')

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Invalid User')
            return redirect('signin')
    return render(request,'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def profile(request,pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_post = Post.objects.filter(user=user_object)
    user_post_length = len(user_post)
    context = {
        'user_obuject':user_object,
        'user_profile' : user_profile,
        'user_post':user_post,
        'user_post_length':user_post_length,
    }
    return render(request,'profile.html',context)