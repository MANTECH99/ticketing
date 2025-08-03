from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import base64
import requests
import base64
import requests
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

def generate_ticket_pdf(ticket):
    # ✅ Utiliser l'URL Cloudinary au lieu du path local
    qr_url = ticket.qr_code.url

    # 🔁 Télécharger l'image depuis Cloudinary
    response = requests.get(qr_url)
    if response.status_code != 200:
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
