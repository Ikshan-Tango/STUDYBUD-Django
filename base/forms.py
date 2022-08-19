from dataclasses import field
from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room #the model on which this form will be working on is the room model
        fields = '__all__' # the fields that this form will have will all be same as in room model
        exclude = ['host' , 'participants'] #we dont want the user to set the host, instead we want the user that creates the room should have its own name and neither do we want to display the participants