import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code(ticket):
    data = f"https://ticketing-production-20dc.up.railway.app/valider-ticket/{ticket.id}/"  # adapte le lien
    print(f"Generating QR code for data: {data}")
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    print(f"QR code generated for ticket {ticket.id}, size: {buffer.tell()} bytes")
    return ContentFile(buffer.getvalue(), name=f"qr_ticket_{ticket.id}.png")
