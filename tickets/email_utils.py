from django.core.mail import EmailMessage

from tickets.pdf_utils import generate_ticket_pdf


def send_ticket_email(ticket):
    print(f"[EMAIL] Envoi de l'email pour {ticket}")
    pdf_data = generate_ticket_pdf(ticket)
    if pdf_data is None:
        print("Erreur génération PDF")
        return False

    email = EmailMessage(
        subject=f"Votre ticket pour {ticket.reservation.event.title}",
        body=f"Bonjour {ticket.reservation.user.username},\n\nVeuillez trouver en pièce jointe votre ticket pour l'événement {ticket.reservation.event.title}.",
        from_email='abdoulahadgueye1999@gmail.com',
        to=[ticket.reservation.user.email],
    )
    email.attach(f'ticket_{ticket.id}.pdf', pdf_data, 'application/pdf')
    email.send()
    return True


