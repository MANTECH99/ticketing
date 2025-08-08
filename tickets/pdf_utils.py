import pdfkit
import base64
import os
import requests
from django.conf import settings
from django.template.loader import render_to_string
from cloudinary.utils import cloudinary_url

def generate_ticket_pdf(ticket, request):
    """
    Génère un PDF de ticket en utilisant wkhtmltopdf et Cloudinary pour les images.
    Compatible Windows/Linux et conserve toutes les options et le debug.
    """
    try:
        # 1. Récupérer l'URL Cloudinary du QR code
        public_id = str(ticket.qr_code)
        qr_url, _ = cloudinary_url(public_id)

        # 2. Télécharger l'image depuis Cloudinary et encoder en base64
        response = requests.get(qr_url)
        response.raise_for_status()
        qr_base64 = base64.b64encode(response.content).decode()

        # 3. Rendre le template HTML
        html_string = render_to_string('tickets/ticket_pdf.html', {
            'ticket': ticket,
            'qr_base64': qr_base64,
            'request': request,
        })

        # 4. Options wkhtmltopdf
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

        # 5. Config wkhtmltopdf (adapter chemin si Linux)
        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        )

        # 6. Générer le PDF
        pdf = pdfkit.from_string(
            html_string,
            False,
            options=options,
            configuration=config
        )
        return pdf

    except Exception as e:
        # Sauvegarde du HTML pour debug
        debug_path = os.path.join(settings.BASE_DIR, 'ticket_debug.html')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html_string if 'html_string' in locals() else '')
        raise Exception(
            f"Erreur lors de la génération du PDF. HTML sauvegardé à {debug_path}. Erreur originale: {str(e)}"
        )
