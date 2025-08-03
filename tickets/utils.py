import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code(ticket):
    data = f"https://ticketing-production-20dc.up.railway.app//valider-ticket/{ticket.id}/"  # adapte le lien
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    file = ContentFile(buffer.getvalue(), name=f"qr_ticket_{ticket.id}.png")

    # Sauvegarde dans le champ qr_code → envoie vers Cloudinary
    ticket.qr_code.save(file.name, file)
    ticket.save()
