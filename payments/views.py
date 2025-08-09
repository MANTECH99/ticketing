# views.py
import uuid
import requests
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from events.models import Reservation, Ticket  # modèle à adapter
from tickets.email_utils import send_ticket_email
from tickets.utils import generate_qr_code


@csrf_exempt
def process_orange_payment(request, reservation_id):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()

        # Récupération de la réservation
        reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

        if not phone:
            messages.error(request, "Veuillez entrer un numéro de téléphone.")
            return redirect('confirmation_reservation', reservation_id=reservation.id)

        if len(phone) != 9 or not phone.isdigit():
            messages.error(request, "Le numéro doit contenir 9 chiffres.")
            return redirect('confirmation_reservation', reservation_id=reservation.id)


        payload = {
            "externalTransactionId": str(uuid.uuid4()),
            "serviceCode": "OM_SN_CASHOUT",
            "amount": int(reservation.total_price()),
            "number": phone,
            "callBackURL": f"https://ticketing-production-20dc.up.railway.app/webhook/orange/",
            "successUrl": f"https://ticketing-production-20dc.up.railway.app/events/confirmation/{reservation.id}/",
            "failureUrl": f"https://ticketing-production-20dc.up.railway.app/events/echec/{reservation.id}/",

        }

        headers = {
            "Authorization": f"Bearer {settings.DEXCHANGE_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(settings.DEXCHANGE_API_URL, json=payload, headers=headers)

        try:
            data = response.json()
        except ValueError:
            messages.error(request, "Réponse du service invalide.")
            return redirect('confirmation_reservation', reservation_id=reservation.id)

        transaction = data.get("transaction", {})
        message = transaction.get("message") or data.get("message") or ""
        message = message[0] if isinstance(message, list) else str(message)

        if transaction.get("success") is True:
            reservation.external_transaction_id = payload["externalTransactionId"]
            reservation.payment_status = "en_cours"
            reservation.payment_method = "orange"  # ⬅️ Ajout ici
            reservation.save()
            messages.info(request, "Paiement en cours... Validez sur #144#")
        elif "identique" in message.lower():
            messages.warning(request, "Transaction identique détectée.")
        elif "solde" in message.lower():
            messages.error(request, f"Paiement échoué : {message}")
        else:
            messages.info(request, f"ℹ️ {message or 'Paiement en attente.'}")

        return redirect('confirmation_reservation', reservation_id=reservation.id)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from events.models import Reservation
import logging
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def orange_money_webhook(request):
    logger.warning("[WEBHOOK ORANGE] → Requête reçue")

    if request.method != 'POST':
        logger.warning("[WEBHOOK ORANGE] ❌ Méthode invalide (non POST)")
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        logger.warning(f"[WEBHOOK ORANGE] 📦 Payload : {payload}")
    except Exception as e:
        logger.warning(f"[WEBHOOK ORANGE] ❌ Erreur parsing JSON : {str(e)}")
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

    transaction_id = payload.get('externalTransactionId')
    status = payload.get('STATUS') or payload.get('status') or payload.get('transaction', {}).get('status')

    logger.warning(f"[WEBHOOK ORANGE] 🧾 externalTransactionId reçu : {transaction_id}")
    logger.warning(f"[WEBHOOK ORANGE] 📘 status reçu : {status}")

    if not transaction_id or not status:
        logger.warning("[WEBHOOK ORANGE] ❌ Données manquantes")
        return JsonResponse({'error': f'Missing or invalid data: {payload}'}, status=400)

    if status.upper() == 'SUCCESS':
        try:
            reservation = Reservation.objects.get(external_transaction_id=transaction_id)
            reservation.payment_status = "payé"
            reservation.status = "payé"  # ✅ Mise à jour du champ status
            reservation.save()

            # Générer un ticket par place réservée
            for _ in range(reservation.quantity):
                ticket = Ticket.objects.create(
                    reservation=reservation,
                    ticket_type=reservation.ticket_type  # 👈 important
                )
                ticket.qr_code.save(f"qr_{ticket.id}.png", generate_qr_code(ticket))
                ticket.save()
                logger.warning(f"[WEBHOOK ORANGE] 📧 Envoi de l'email pour ticket {ticket.id}")
            logger.warning(f"[WEBHOOK ORANGE] ✅ Paiement confirmé pour la réservation {reservation.id}")
            return JsonResponse({'status': 'updated'}, status=200)
        except Reservation.DoesNotExist:
            logger.warning(f"[WEBHOOK ORANGE] ❌ Aucune réservation trouvée avec ID {transaction_id}")
            return JsonResponse({'error': 'Reservation not found'}, status=404)

    logger.warning("[WEBHOOK ORANGE] ℹ️ Paiement non confirmé ou échec")
    return JsonResponse({'error': f'Unhandled status: {status}'}, status=400)

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import uuid
import requests
from django.conf import settings
from events.models import Reservation

@csrf_exempt
def process_wave_payment(request, reservation_id):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

        # 🔐 Validation du numéro
        if not phone or len(phone) != 9 or not phone.isdigit():
            messages.error(request, "Numéro Wave invalide (9 chiffres attendus).")
            return redirect('confirmation_reservation', reservation_id=reservation.id)

        external_id = str(uuid.uuid4())
        payload = {
            "externalTransactionId": external_id,
            "serviceCode": "WAVE_SN_CASHOUT",  # ⚠️ à confirmer selon DExchange
            "amount": int(reservation.total_price()),
            "number": phone,
            "callBackURL": f"https://ticketing-production-20dc.up.railway.app/webhook/orange/",
            "successUrl": f"https://ticketing-production-20dc.up.railway.app/events/confirmation/{reservation.id}/",
            "failureUrl": f"https://ticketing-production-20dc.up.railway.app/events/echec/{reservation.id}/",

        }

        headers = {
            "Authorization": f"Bearer {settings.DEXCHANGE_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # 📡 Envoi à DExchange
        try:
            response = requests.post(settings.DEXCHANGE_API_URL, json=payload, headers=headers)
            data = response.json()
        except ValueError:
            messages.error(request, "Réponse du service Wave invalide.")
            return redirect('confirmation_reservation', reservation_id=reservation.id)
        except Exception as e:
            messages.error(request, f"Erreur de connexion : {str(e)}")
            return redirect('confirmation_reservation', reservation_id=reservation.id)

        # 🔍 Débogage (réactivé temporairement)
        #messages.error(request, f"Réponse API : {data}")

        # Analyse de la réponse
        transaction = data.get("transaction", {})
        redirect_url = data.get("redirectUrl") or transaction.get("redirectUrl") or transaction.get(
            "deepLink") or transaction.get("cashout_url")
        message = transaction.get("message") or data.get("message") or "Erreur inconnue."

        if not redirect_url:
            messages.error(request, f"Échec du paiement : {message}")
            return redirect('confirmation_reservation', reservation_id=reservation.id)

        # ✅ Mise à jour de la réservation
        reservation.external_transaction_id = external_id
        reservation.payment_method = "wave"
        reservation.payment_status = "en_cours"
        reservation.save()

        return redirect(redirect_url)


@csrf_exempt
def wave_webhook(request):
    logger.warning("[WEBHOOK WAVE] → Requête reçue")

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        logger.warning(f"[WEBHOOK WAVE] 📦 Payload : {payload}")
    except Exception as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

    transaction_id = payload.get('externalTransactionId')
    status = payload.get('status') or payload.get('transaction', {}).get('status')

    if not transaction_id or not status:
        return JsonResponse({'error': 'Missing data'}, status=400)

    if status.upper() == 'SUCCESS':
        try:
            reservation = Reservation.objects.get(external_transaction_id=transaction_id)
            reservation.payment_status = "payé"
            reservation.status = "payé"
            reservation.save()

            for _ in range(reservation.quantity):
                ticket = Ticket.objects.create(
                    reservation=reservation,
                    ticket_type=reservation.ticket_type  # 👈 important
                )
                ticket.qr_code.save(f"qr_{ticket.id}.png", generate_qr_code(ticket))
                ticket.save()
            return JsonResponse({'status': 'updated'}, status=200)
        except Reservation.DoesNotExist:
            return JsonResponse({'error': 'Reservation not found'}, status=404)

    return JsonResponse({'error': f'Unhandled status: {status}'}, status=400)
