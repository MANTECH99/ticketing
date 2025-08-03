from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import base64
import requests

def generate_ticket_pdf(ticket):
    # Lire le QR code depuis Cloudinary via son URL
    try:
        response = requests.get(ticket.qr_code.url)
        response.raise_for_status()
    except Exception as e:
        print("Erreur lors du téléchargement du QR code :", e)
        return None

    encoded_string = base64.b64encode(response.content).decode()

    html_string = render_to_string('tickets/ticket_pdf.html', {
        'ticket': ticket,
        'qr_base64': encoded_string,
    })
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)
    if pisa_status.err:
        return None
    return pdf_file.getvalue()
