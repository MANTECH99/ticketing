from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('reserver/<int:event_id>/', views.reserver_ticket, name='reserver_ticket'),

    path('confirmation/<int:reservation_id>/', views.confirmation_reservation, name='confirmation_reservation'),
    path('creer/', views.creer_event, name='creer_event'),
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/event/<int:event_id>/tickets/', views.voir_tickets_event, name='voir_tickets_event'),
    path('agent/scan/', views.scan_ticket, name='scan_ticket'),
    path('events/rapport/pdf/<int:event_id>/', views.rapport_pdf_event, name='rapport_pdf_event'),
    path('modifier/<int:event_id>/', views.modifier_event, name='modifier_event'),

# urls.py
    path('events/<int:event_id>/ajouter-type/', views.ajouter_ticket_type, name='ajouter_ticket_type'),
    path('events', views.rapport, name='liste_rapport'),




]
