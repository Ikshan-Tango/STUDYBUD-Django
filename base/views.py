from cmath import log
from email import message
from multiprocessing import context
from pickle import FALSE
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# rooms=[
#     {'id':'1','name':'lets learn python'},
#     {'id':'2','name':'design with me'},
#     {'id':'3','name':'front end developers'},
# ]

# Create your views here.

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST': #loads the data of user credentials from the form 
        username = request.POST.get('username').lower()
        password =  request.POST.get('password')

        try:
            user=User.objects.get(username=username)
        except:
             messages.error(request, "Error: User does not exist")
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
             messages.error(request, "Error: Username or password does not exist")
       

    context= {"page":page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()#this is a form made by django itself which can be styles as well later

    if request.method == "POST":

        form = UserCreationForm(request.POST) # this contains the usernamea and password what the user sends in
        
        if form.is_valid():
            user = form.save(commit = False) #if for some reason the user added in like a upper case in their or they capitalize their name or maybe their email depending on how they're registering we want to make sure that that's lowercase automatically so we want to be able to clean we actually want to be able to clean this data, so we use commit = false to basically freeze the saving to clean the data before we post it
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occured during registration")


    context = {"form":form}
    return render(request,"base/login_register.html",context)

def home(request):
    #return HttpResponse('Home page')
    #making the dynamic search bar 
    q=request.GET.get('q') if request.GET.get('q')!= None else '' #this line is respoonsible to get the room name based on the query that is searched ..... and .filter() function loads the data only what is specified in its arguments
    # by using Q we are implementing a dynamic search engine which can search for messages, specific room and topic name as well
    #if i remove this if and else statement or use it afterwards then it will give an error
    rooms=Room.objects.filter(Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q) 
    ) 

    topics = Topic.objects.all()[0:5] #loading all the topics in this topic variable and [0:5] means that it will only load the first 5 topics and that's how we can limit

    room_count = rooms.count()

    #for making the activity feed :-
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) #when a room is selected from the left side then the activity feed will show recent acitivity only of that particular room and not of all rooms, in Messages model there is room , then in Room model there is topic then in Topic model there is name, thats how we query the topic name from the Message models
    context={'rooms':rooms, 'topics':topics, 'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request, pk):
    # room=None #setting a variable named as room to empty 

    # for i in rooms:
    #     if i['id'] == int(pk): #if an elements id of the rooms dictionary matches with its url  
    #         room=i

    room=Room.objects.get(id=pk)
    room_messages= room.message_set.all() #message_set.all() loads all the messages from the MESSAGE model which are only linked with the particular room id, remember that in this case message is all lowercase whereas model was Message, used in many to many relationships
    participants = room.participants.all() #

    if request.method == 'POST':#this is for the comment that a participant can add
        message = Message.objects.create( #this is a unique method and we are using it for the firs time, using this method we can get message from the user and send it to our model as well while setting its other attributes like user and room to which the message belongs to
            user = request.user,
            room = room,
            body = request.POST.get('body')#it  will recieve the messgage that was entered in the message box
        )

        room.participants.add(request.user) #this line will add the participant to the model 
        return redirect('room',pk=room.id)

    context={'room':room,'room_messages':room_messages, 'participants':participants}
    return render(request,'base/room.html',context)

def userProfile(request, pk):
    user = User.objects.get(id = pk)

    rooms = user.room_set.all() #remember we can get all the children of a specific object by doing the model name and then underscore set and then whatever we want there so in this case we're getting all of them, in this case parent is the user and children are the rooms that are linked with the particular user

    room_messages = user.message_set.all()
    
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'topics':topics,'room_messages':room_messages}
    return render(request,'base/profile.html',context)

@login_required(login_url='login') 
def createRoom(request): #this view add the room/ text with details of the form added to main page
    form = RoomForm
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name = topic_name) #in the arguments there is name = topic_name, left side name is of the model Topic and right side is the html class name of the attribute
        Room.objects.create( # this must be pretty understandable on its own, WE are creaTING all the objects for the room model
            host = request.user,
            topic = topic, #LEFT TOPIC is of the room model , RIGHT TOPIC is the topic which was created up above
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )

        return redirect('home')
        # form = RoomForm(request.POST)#this takes the recent data that we have added in the room
        # if form.is_valid():
        #     room = form.save(commit= False)# this loads the data in a buffer region before actually saving it  as we use commit = false
        #     room.host = request.user  #we are making request.user the room host as he is the one who is creating the form
        #     room.save()
        #     return redirect('home')

    context = {'form': form, 'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login') 
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # this form will be filled with the values of the room we click so that we can edit it

    topics = Topic.objects.all()
    
    if request.user != room.host: #if the user who's logged in, is not the room host/ the owner of the room, then he should not be able to edit or delete others owners rooms so for handling that we are using this
        return HttpResponse("You're not allowed here!!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name = topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

        
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')

    context={'form':form,'topics':topics, 'room':room}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login') 
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk) #load that data from the model which has the id=pk 
    if request.user != room.host:
        return HttpResponse("You're not allowed here!!")
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context={'obj':room}
    return render(request,'base/delete.html',context)


@login_required(login_url='login') 
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk) #load that data from the model which has the id=pk 
    if request.user != message.user:
        return HttpResponse("You're not allowed here!!")
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    context={'obj':message}
    return render(request,'base/delete.html',context)


@login_required(login_url='login') 
def updateUser(request):
    user = request.user
    form = UserForm(instance=user) 

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk = user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html',context)


def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q')!= None else '' 
    topics=Topic.objects.filter(name__icontains=q) 

    #topics = Topic.objects.all() #loading all the topics in this topic variable 

    topics_count = topics.count()

    context={'topics':topics, 'topics_count':topics_count}
    return render(request,'base/topics.html',context)

def activityPage(request):

    room_messages=Message.objects.all()
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)