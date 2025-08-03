from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import base64
import requests

def generate_ticket_pdf(ticket):
    try:
        response = requests.get(ticket.qr_code.url)
        response.raise_for_status()
        encoded_string = base64.b64encode(response.content).decode()
    except Exception as e:
        print("Erreur téléchargement QR code :", e)
        return None

    try:
        html_string = render_to_string('tickets/ticket_pdf.html', {
            'ticket': ticket,
            'qr_base64': encoded_string,
        })

        print("[DEBUG] HTML généré :\n", html_string)  # Facultatif mais utile pour voir le rendu

        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(src=html_string, dest=pdf_file)

        if pisa_status.err:
            print("[ERREUR PDF]", pisa_status.err)
            return None
        return pdf_file.getvalue()

    except Exception as e:
        print("Erreur génération PDF :", e)
        return None
