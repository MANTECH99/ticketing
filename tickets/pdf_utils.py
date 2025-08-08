import os
import platform
import pdfkit
import base64
import requests
from django.conf import settings
from django.template.loader import render_to_string
from cloudinary.utils import cloudinary_url

def generate_ticket_pdf(ticket, request):
    """
    Génère un PDF (bytes) pour un ticket en utilisant wkhtmltopdf (via pdfkit).
    - Ticket QR est récupéré depuis Cloudinary et encodé en base64.
    - request doit être passé pour permettre les URLs absolues dans le template.
    - Retourne les bytes du PDF ou soulève une exception (HTML sauvegardé pour debug).
    """
    html_string = ''  # garantit l'existence en cas d'exception
    try:
        # 1) Récupérer l'URL Cloudinary et encoder le QR en base64
        public_id = str(ticket.qr_code)
        qr_url, _ = cloudinary_url(public_id)
        resp = requests.get(qr_url)
        resp.raise_for_status()
        qr_base64 = base64.b64encode(resp.content).decode()

        # 2) Rendre le template (passer request pour construire des URLs absolues)
        html_string = render_to_string('tickets/ticket_pdf.html', {
            'ticket': ticket,
            'qr_base64': qr_base64,
            'request': request,
        })

        # 3) Options wkhtmltopdf (ajuste selon besoin)
        options = {
            'enable-local-file-access': None,   # permet accès fichiers locaux si utilisés
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

        # 4) Chemin du binaire wkhtmltopdf (var env > Windows path > Linux path)
        wk_cmd = os.environ.get('WKHTMLTOPDF_CMD')
        if not wk_cmd:
            if platform.system() == "Windows":
                wk_cmd = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            else:
                # chemins courants, adapte si nécessaire (/usr/bin ou /usr/local/bin)
                wk_cmd = "/usr/bin/wkhtmltopdf" if os.path.exists("/usr/bin/wkhtmltopdf") else "/usr/local/bin/wkhtmltopdf"

        config = pdfkit.configuration(wkhtmltopdf=wk_cmd)

        # 5) Génération du PDF (retourne bytes)
        pdf_bytes = pdfkit.from_string(html_string, False, options=options, configuration=config)
        return pdf_bytes

    except Exception as e:
        # Sauvegarde du HTML pour debug (chemin accessible en prod)
        try:
            debug_path = os.path.join(settings.BASE_DIR, 'ticket_debug.html')
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_string or '')
        except Exception:
            # Ne pas masquer l'erreur principale si la sauvegarde échoue
            pass
        raise RuntimeError(f"Erreur lors de la génération du PDF. HTML sauvegardé (si possible). Erreur originale: {str(e)}")
