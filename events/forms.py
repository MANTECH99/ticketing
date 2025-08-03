from django import forms
from .models import Event, TicketType


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'total_tickets', 'type', 'image']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }



class TicketTypeForm(forms.ModelForm):
            class Meta:
                model = TicketType
                fields = ['name', 'price']

