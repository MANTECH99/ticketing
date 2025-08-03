from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import base64

def generate_ticket_pdf(ticket):
    # Lire le QR code en base64 pour l'inclure dans le HTML
    # Lire le contenu du fichier depuis Cloudinary (ou local)
    qr_file = ticket.qr_code
    encoded_string = base64.b64encode(qr_file.read()).decode()

    html_string = render_to_string('tickets/ticket_pdf.html', {
        'ticket': ticket,
        'qr_base64': encoded_string,
    })
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)
    if pisa_status.err:
        return None
    return pdf_file.getvalue()

