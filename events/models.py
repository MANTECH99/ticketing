from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Event(models.Model):
    EVENT_TYPES = [
        ('concert', 'Concert'),
        ('cinema', 'Cinéma'),
        ('autre', 'Autre'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    total_tickets = models.PositiveIntegerField()
    image = CloudinaryField('image', blank=True, null=True)
    type = models.CharField(max_length=20, choices=EVENT_TYPES, default='autre')

    @property
    def is_free(self):
        # Un événement est gratuit si tous ses types de tickets ont un prix de 0
        return all(ticket_type.price == 0 for ticket_type in self.ticket_types.all())

    @property
    def lowest_ticket_price(self):
        ticket_types = self.ticket_types.all()
        if not ticket_types.exists():
            return None  # ou 0 si tu préfères
        return min(t.price for t in ticket_types)

    def __str__(self):
        return self.title

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=50)  # Ex: simple, VIP, etc.
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.event.title} ({self.price} F)"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)  # 👈 à ajouter
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('en_attente', 'En attente'), ('payé', 'Payé')], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    # ... autres champs
    payment_status = models.CharField(max_length=20, choices=[('non_payé', 'Non payé'), ('payé', 'Payé')],
                                      default='non_payé')
    external_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('orange', 'Orange Money'),
        ('wave', 'Wave')
    ], null=True, blank=True)

    def total_price(self):
        return self.quantity * self.ticket_type.price  # ✅ prix par type




class Ticket(models.Model):
    reservation = models.ForeignKey('Reservation', on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)

    qr_code = CloudinaryField('qr_code', blank=True, null=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ticket_type.name} - {self.reservation.event.title} - Ticket {self.id}"




