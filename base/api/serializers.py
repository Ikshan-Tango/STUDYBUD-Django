#serializers are just like models but in API's
from csv import field_size_limit
from rest_framework.serializers import ModelSerializer

from base.models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
        
