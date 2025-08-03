from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .pdf_utils import generate_ticket_pdf
from events.models import Ticket

@login_required
def telecharger_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id, reservation__user=request.user)
    pdf_content = generate_ticket_pdf(ticket)
    if pdf_content is None:
        return HttpResponse("Erreur lors de la génération du PDF.", status=500)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response
