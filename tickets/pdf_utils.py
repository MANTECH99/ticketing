from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import base64
import requests
from cloudinary.utils import cloudinary_url

def generate_ticket_pdf(ticket):
    if not ticket.qr_code:
        print("Pas de QR code.")
        return None

    try:
        # Convertir en string pour avoir le public_id
        public_id = str(ticket.qr_code)

        # Générer l'URL complète à partir du public_id
        qr_url, _ = cloudinary_url(public_id)

        print("QR Code URL:", qr_url)  # debug

        # Télécharger l'image depuis Cloudinary
        response = requests.get(qr_url)
        response.raise_for_status()

        encoded_string = base64.b64encode(response.content).decode()

        html_string = render_to_string('tickets/ticket_pdf.html', {
            'ticket': ticket,
            'qr_base64': encoded_string,
        })

        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)

        if pisa_status.err:
            print("[ERREUR PDF] La génération du PDF a échoué")
            return None

        return pdf_file.getvalue()

    except Exception as e:
        print("[ERREUR PDF] Exception :", e)
        return None
