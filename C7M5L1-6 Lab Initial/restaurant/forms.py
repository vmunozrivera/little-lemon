
# Django
from django.forms import ModelForm

# Models
from .models import Booking


class BookingForm(ModelForm):
    
    class Meta:
        model = Booking
        fields = "__all__"


