

from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
import base64
import os
from django.conf import settings
from weasyprint import HTML, CSS


def generate_ticket_pdf(ticket):
    # Lire le QR code en base64
    qr_path = ticket.qr_code.path
    with open(qr_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Génération du HTML à partir du template
    html_string = render_to_string('tickets/ticket_pdf.html', {
        'ticket': ticket,
        'qr_base64': encoded_string,
        'fontawesome_css_path': os.path.join(settings.BASE_DIR, 'static/fontawesome/css/all.min.css'),
    })
    # Chemin absolu vers le CSS
    css_path = os.path.join(settings.BASE_DIR, 'static/css/style.css')
    # Génération PDF avec WeasyPrint
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(
        pdf_file,
        stylesheets=[
            CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/style.css')),
            CSS(filename=os.path.join(settings.BASE_DIR, 'static/fontawesome/css/all.min.css')),    ]
    )
    return pdf_file.getvalue()
