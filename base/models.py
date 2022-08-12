from pickle import TRUE
from turtle import ondrag
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=TRUE)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=TRUE)# A room can have only one topic
    name=models.CharField(max_length=200)
    description=models.TextField(null=True, blank = True) #black =true means that if we make it a form then this feild can still be empty and not give any error
    participants =  models.ManyToManyField(User, related_name='participants', blank=True) #we are creating a many to many field 
    updated= models.DateTimeField(auto_now=True) # auto now = true takes a snapshot everytime we save 
    created = models.DateTimeField(auto_now_add=True)# auto now add= true takes only the snapshot at the first instance and after that even if we save again, it wont take another snapshot

    class Meta:
        ordering = ['-updated','-created'] #we do this to make sure that when we opst anything using the room_frm, the newst thingy comes at the top

    def __str__(self):
        return self.name

# we are building a one to many relationship here, i.e a user can have many messages but a message can have only one user

class Message(models.Model): #the chatbot messages model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room =  models.ForeignKey(Room, on_delete=models.CASCADE) #this establishes a relationship between the parent model i.e the room and a child model which in this case is the message model, and ondelete we are cascading it i.e deleting all the messages if a room is deleted
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created'] 

    def __str__(self):
        return self.body[0:50]