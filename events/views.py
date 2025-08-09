from django.shortcuts import render

from tickets.email_utils import send_ticket_email
from tickets.utils import generate_qr_code
from .models import Event
from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Reservation
from django.contrib.auth.decorators import login_required, user_passes_test


def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def rapport(request):
    events = Event.objects.all()
    return render(request, 'events/rapport.html', {'events': events})


from .models import TicketType, Ticket, Reservation, Event
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from tickets.pdf_utils import generate_ticket_pdf


@login_required
def reserver_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    ticket_types = TicketType.objects.filter(event=event)

    # Vérifier les réservations existantes de cet utilisateur pour cet événement
    existing_reservations = Reservation.objects.filter(user=request.user, event=event)
    total_reserved_by_user = sum(r.quantity for r in existing_reservations)

    if request.method == 'POST':
        # 🔹 Champs utilisateur depuis le formulaire
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        quantity = int(request.POST.get('quantity'))

        # 🔹 Mettre à jour les infos utilisateur si elles ont changé
        user = request.user
        changed = False
        if first_name and first_name != user.first_name:
            user.first_name = first_name
            changed = True
        if last_name and last_name != user.last_name:
            user.last_name = last_name
            changed = True
        if email and email != user.email:
            user.email = email
            changed = True
        if changed:
            user.save()

        ticket_type_id = request.POST.get('ticket_type')
        try:
            selected_type = TicketType.objects.get(id=ticket_type_id, event=event)
        except (TicketType.DoesNotExist, TypeError):
            # Type de ticket invalide ou non sélectionné
            return render(request, 'events/reserver_ticket.html', {
                'event': event,
                'ticket_types': ticket_types,
                'error': "Type de ticket invalide ou non sélectionné."
            })

        # Limite si le type de ticket est gratuit
        if selected_type.price == 0:
            max_per_user = 100  # Ajuste cette limite si besoin
            if total_reserved_by_user + quantity > max_per_user:
                return render(request, 'events/reserver_ticket.html', {
                    'event': event,
                    'ticket_types': ticket_types,
                    'error': f"Événement gratuit : vous ne pouvez réserver que {max_per_user} places maximum."
                })

        if quantity <= 0 or quantity > event.total_tickets:
            return render(request, 'events/reserver_ticket.html', {
                'event': event,
                'ticket_types': ticket_types,
                'error': 'Quantité invalide ou nombre de tickets insuffisant.'
            })

        reservation = Reservation.objects.create(
            user=request.user,
            event=event,
            quantity=quantity,
            ticket_type=selected_type,  # 👈 important
            status='payé' if selected_type.price == 0 else 'en_attente',
            payment_status='payé' if selected_type.price == 0 else 'non_payé'
        )

        event.total_tickets -= quantity
        event.save()

        # Si le type de ticket est gratuit, générer directement les tickets
        if selected_type.price == 0:
            for _ in range(reservation.quantity):
                # Étape 1 : Créer le ticket sans QR code
                ticket = Ticket.objects.create(reservation=reservation, ticket_type=selected_type)
                # Étape 2 : Générer le QR code
                qr_image_file = generate_qr_code(ticket)
                print("qr_image_file:", qr_image_file, type(qr_image_file))
                if not qr_image_file:
                    # Gérer l'erreur ou afficher un message d'erreur
                    return render(request, 'events/reserver_ticket.html', {
                        'event': event,
                        'ticket_types': ticket_types,
                        'error': "Erreur lors de la génération du QR code."
                    })
        
                # Étape 3 : Uploader sur Cloudinary
                import cloudinary.uploader
                upload_result = cloudinary.uploader.upload(qr_image_file, folder='qr_codes')
                
                # Étape 4 : Mettre à jour le champ CloudinaryField avec le public_id
                ticket.qr_code = upload_result['public_id']
                ticket.save()
        
                # Étape 4 : Générer le PDF (à partir du ticket qui a maintenant un QR)
                pdf_bytes = generate_ticket_pdf(ticket, request)
        
                # Étape 5 : Envoyer l'email avec pièce jointe PDF
                #send_ticket_email(ticket, pdf_bytes)

        # Redirection vers une page de confirmation
        return redirect('confirmation_reservation', reservation.id)

    return render(request, 'events/reserver_ticket.html', {
        'event': event,
        'ticket_types': ticket_types
    })



def confirmation_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'events/confirmation.html', {'reservation': reservation})


from .forms import EventForm
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required  # Seuls les admins connectés peuvent créer
def creer_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)  # 🔁 ICI on ajoute request.FILES
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/creer_event.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Event
from .forms import EventForm


@staff_member_required
def modifier_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # ou la page que tu veux
    else:
        form = EventForm(instance=event)

    return render(request, 'events/modifier_event.html', {'form': form, 'event': event})


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Event

@staff_member_required
def dashboard_admin(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'events/dashboard_admin.html', {'events': events})


from events.models import Ticket

@staff_member_required
def voir_tickets_event(request, event_id):
    tickets = Ticket.objects.filter(reservation__event__id=event_id).select_related('reservation', 'reservation__user')
    event = Event.objects.get(id=event_id)
    return render(request, 'events/tickets_par_event.html', {'event': event, 'tickets': tickets})


# views.py
from django.shortcuts import render, get_object_or_404
from .models import Ticket



from django.shortcuts import render

@user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser))
def scan_ticket(request):
    return render(request, 'events/scan.html')

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Event, Reservation

def rapport_pdf_event(request, event_id):
    event = Event.objects.get(id=event_id)
    reservations = Reservation.objects.filter(event=event)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_event_{event.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Rapport Réservations pour l'événement : {event.title}")

    p.setFont("Helvetica", 12)
    y = height - 80

    # Positions décalées
    p.drawString(50, y, "Utilisateur")      # Large colonne à gauche
    p.drawString(280, y, "Quantité")        # décalé
    p.drawString(360, y, "Statut")          # décalé
    p.drawString(460, y, "Prix total")      # décalé

    y -= 20

    for res in reservations:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)

        p.drawString(50, y, str(res.user.username))
        p.drawString(280, y, str(res.quantity))
        p.drawString(360, y, res.status)
        p.drawString(460, y, f"{res.total_price()} F")
        y -= 20

    p.showPage()
    p.save()
    return response


# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TicketTypeForm
from .models import Event

@staff_member_required
def ajouter_ticket_type(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = TicketTypeForm(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event = event  # on lie le type à l'événement
            ticket_type.save()
            return redirect('event_list')  # ou autre
    else:
        form = TicketTypeForm()

    return render(request, 'events/ajouter_ticket_type.html', {'form': form, 'event': event})




from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test

@staff_member_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "L'événement a été supprimé avec succès.")
    return redirect('event_list')  # adapte le nom de ta vue de liste d'événements

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Reservation  # adapte selon ton app

@staff_member_required
def liste_reservations(request):
    reservations = Reservation.objects.select_related('event', 'user').order_by('-created_at')
    return render(request, 'events/liste_reservations.html', {'reservations': reservations})


@staff_member_required
def supprimer_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.delete()
    messages.success(request, "Réservation supprimée avec succès.")
    return redirect('liste_reservations')




from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
import cloudinary.uploader
from tickets.email_utils import send_ticket_email
from tickets.pdf_utils import generate_ticket_pdf
from tickets.utils import generate_qr_code
@login_required
def envoyer_tickets_email(request, reservation_id):
    """Vue dédiée uniquement à l'envoi des tickets par email"""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Vérification de sécurité
    if reservation.user != request.user:
        raise PermissionDenied("Vous n'avez pas accès à cette réservation")

    # Vérifier qu'il y a des tickets
    tickets = reservation.ticket_set.all()
    if not tickets.exists():
        messages.error(request, "Aucun ticket à envoyer")
        return redirect('confirmation_reservation', reservation.id)

    try:
        # Envoyer chaque ticket par email
        for ticket in tickets:
            # Si le ticket n'a pas de QR code (au cas où)
            if not ticket.qr_code:
                # Générer le QR code
                qr_image_file = generate_qr_code(ticket)
                
                # Uploader sur Cloudinary
                upload_result = cloudinary.uploader.upload(qr_image_file, folder='qr_codes')
                ticket.qr_code = upload_result['public_id']
                ticket.save()
            
            # Générer le PDF
            pdf_bytes = generate_ticket_pdf(ticket)
            
            # Envoyer l'email avec le PDF en pièce jointe
            send_ticket_email(ticket, pdf_bytes)

        messages.success(request, "Vos tickets ont été envoyés par email avec succès!")
    except Exception as e:
        # Logger l'erreur ici si vous avez un système de logging
        messages.error(request, f"Une erreur est survenue lors de l'envoi des tickets: {str(e)}")

    return redirect('confirmation_reservation', reservation.id)

import pdfkit
from django.http import HttpResponse

def test_wkhtml(request):
    # Contenu HTML simple
    html_content = "<h1>Test wkhtmltopdf</h1><p>Si tu vois ça en PDF, ça marche !</p>"

    try:
        # Générer PDF à partir du HTML
        pdf = pdfkit.from_string(html_content, False)
    except OSError as e:
        return HttpResponse(f"Erreur wkhtmltopdf : {e}")

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="test_wkhtml.pdf"'
    return response


import subprocess
from django.http import HttpResponse

def test_wkhtml_path(request):
    try:
        path = subprocess.check_output(['which', 'wkhtmltopdf']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        path = "wkhtmltopdf not found"
    return HttpResponse(f"Chemin wkhtmltopdf: {path}")

