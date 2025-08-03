from django.urls import path
from . import views

urlpatterns = [
    path('paiement/orange/<int:reservation_id>/', views.process_orange_payment, name='process_orange_payment'),
    path('webhook/orange/', views.orange_money_webhook, name='webhook_orange'),

    path('paiement/wave/<int:reservation_id>/', views.process_wave_payment, name='process_wave_payment'),
    path('webhook/wave/', views.wave_webhook, name='wave_webhook'),
]
