import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code(ticket):
    data = f"https://ticketing-production-20dc.up.railway.app/valider-ticket/{ticket.id}/"
    print(f"Generating QR code for data: {data}")
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)  # <-- important de remettre le curseur au début
    content_file = ContentFile(buffer.read(), name=f"qr_ticket_{ticket.id}.png")
    print(f"QR code generated for ticket {ticket.id}, size: {content_file.size} bytes")
    return content_file
