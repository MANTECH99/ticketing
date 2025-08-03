from django.shortcuts import render, get_object_or_404
from events.models import Ticket

def valider_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.used:
        message = "❌ Ce ticket a déjà été utilisé."
        statut = "invalide"
    elif ticket.reservation.payment_status != 'payé':
        message = "❌ Ce ticket n'est pas encore payé."
        statut = "invalide"
    else:
        ticket.used = True
        ticket.save()
        message = "✅ Ticket valide. Entrée autorisée."
        statut = "valide"

    return render(request, 'entry_validation/entry_validation.html', {
        'ticket': ticket,
        'message': message,
        'statut': statut,
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from events.models import Ticket, Event

@staff_member_required
def tickets_a_valider(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(
        reservation__event=event,
        reservation__payment_status='payé',
        used=False
    ).select_related('reservation__user')
    return render(request, 'entry_validation/liste_a_valider.html', {'event': event, 'tickets': tickets})


@staff_member_required
def valider_manuellement(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.used:
        message = "Ce ticket a déjà été utilisé."
    elif ticket.reservation.payment_status != 'payé':
        message = "Ce ticket n'est pas encore payé."
    else:
        ticket.used = True
        ticket.save()
        message = "✅ Ticket validé avec succès."

    return redirect('tickets_a_valider', event_id=ticket.reservation.event.id)


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def events_pour_validation(request):
    events = Event.objects.all()
    return render(request, 'events/events_pour_validation.html', {'events': events})
