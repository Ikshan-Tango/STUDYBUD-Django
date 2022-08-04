from dataclasses import field
from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room #the model on which this form will be working on is the room model
        fields = '__all__' # the fields that this form will have will all be same as in room model