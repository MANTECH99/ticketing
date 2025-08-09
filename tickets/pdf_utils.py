import pdfkit
import base64
import os
from django.conf import settings
from django.template.loader import render_to_string


def generate_ticket_pdf(ticket, request):
    """
    Génère un PDF de ticket avec wkhtmltopdf (pdfkit) en utilisant les fichiers locaux.
    Compatible Docker/Linux.
    """
    # 1. Encoder le QR code en base64 (chemin local)
    with open(ticket.qr_code.path, "rb") as image_file:
        qr_base64 = base64.b64encode(image_file.read()).decode()

    # 2. Rendre le template HTML
    html_string = render_to_string('tickets/ticket_pdf.html', {
        'ticket': ticket,
        'qr_base64': qr_base64,
        'request': request,
    })

    # 3. Options wkhtmltopdf
    options = {
        'enable-local-file-access': None,
        'quiet': '',
        'no-stop-slow-scripts': '',
        'encoding': "UTF-8",
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'disable-smart-shrinking': '',
    }

    # 4. Config Linux/Docker
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

    # 5. Génération du PDF
    try:
        pdf = pdfkit.from_string(
            html_string,
            False,  # Retourner en mémoire
            options=options,
            configuration=config
        )
        return pdf
    except Exception as e:
        debug_path = os.path.join(settings.BASE_DIR, 'ticket_debug.html')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html_string)
        raise Exception(
            f"Erreur lors de la génération du PDF. HTML sauvegardé à {debug_path}. Erreur originale: {str(e)}"
        )
