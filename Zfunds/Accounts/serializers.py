from rest_framework import serializers
from .models import CustomUser, Advisor

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'mobile', 'password', "otp", "role"]

    
class AdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor
        fields = "__all__"
