
# Django
from django.contrib.auth.models import User

# DRF 
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# Models
from .models import Rating


class RatingSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        default = serializers.CurrentUserDefault()
    )

    class Meta:
        model = Rating
        fields = ['user', 'menuitem_id', 'rating']
        validators = [
            UniqueTogetherValidator(
                queryset = Rating.objects.all(),
                fields = ['user', 'menuitem_id', 'rating']    
            )
        ]
        extra_kwargs = {
            'rating': { 'max_value': 5, 'min_value': 0 }
        }