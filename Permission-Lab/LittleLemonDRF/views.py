
# DRF
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Models
from .models import Rating

# Serializer
from .serializer import RatingSerializers


class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializers

    def get_permissions(self):
        
        if self.request.method == 'GET':
            return []

        return [IsAuthenticated()]
        
