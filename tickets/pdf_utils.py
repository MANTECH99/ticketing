import os
import platform
import pdfkit
import base64
import requests
from django.conf import settings
from django.template.loader import render_to_string
from cloudinary.utils import cloudinary_url

def find_wkhtmltopdf():
    """
    Cherche wkhtmltopdf dans plusieurs chemins courants,
    et dans la variable d'environnement WKHTMLTOPDF_CMD.
    """
    # Priorité à la variable d'environnement
    env_path = os.environ.get('WKHTMLTOPDF_CMD')
    if env_path and os.path.exists(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # Sur Windows, chemin classique
    if platform.system() == "Windows":
        win_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        if os.path.exists(win_path) and os.access(win_path, os.X_OK):
            return win_path

    # Sur Linux, chemins fréquents
    linux_paths = [
        "/usr/bin/wkhtmltopdf",
        "/usr/local/bin/wkhtmltopdf",
        "/snap/bin/wkhtmltopdf",  # au cas où installé par snap
    ]
    for path in linux_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    raise RuntimeError("wkhtmltopdf executable not found. Vérifie installation et variable WKHTMLTOPDF_CMD.")

def generate_ticket_pdf(ticket, request):
    html_string = ''
    try:
        # 1) Récupérer QR code Cloudinary encodé
        public_id = str(ticket.qr_code)
        qr_url, _ = cloudinary_url(public_id)
        resp = requests.get(qr_url)
        resp.raise_for_status()
        qr_base64 = base64.b64encode(resp.content).decode()

        # 2) Rendre template
        html_string = render_to_string('tickets/ticket_pdf.html', {
            'ticket': ticket,
            'qr_base64': qr_base64,
            'request': request,
        })

        # 3) Options wkhtmltopdf
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

        # 4) Trouver wkhtmltopdf
        wk_cmd = find_wkhtmltopdf()
        config = pdfkit.configuration(wkhtmltopdf=wk_cmd)

        # 5) Générer PDF
        pdf_bytes = pdfkit.from_string(html_string, False, options=options, configuration=config)
        return pdf_bytes

    except Exception as e:
        try:
            debug_path = os.path.join(settings.BASE_DIR, 'ticket_debug.html')
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_string or '')
        except Exception:
            pass
        raise RuntimeError(f"Erreur lors de la génération du PDF. HTML sauvegardé (si possible). Erreur originale: {str(e)}")
