import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code(ticket):
    data = f"https://19dacf9b9c22.ngrok-free.app/valider-ticket/{ticket.id}/"  # adapte le lien
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f"qr_ticket_{ticket.id}.png")
