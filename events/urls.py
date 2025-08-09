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
        path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
path('events/reservations/', views.liste_reservations, name='liste_reservations'),
path('events/reservation/<int:reservation_id>/delete/', views.supprimer_reservation, name='supprimer_reservation'),
path('reservation/<int:reservation_id>/envoyer-tickets/', views.envoyer_tickets_email, name='envoyer_tickets_email'),
        path('test-wkhtml/', views.test_wkhtml, name='test_wkhtml'),
    path('test-wkhtml-path/', test_wkhtml_path, name='test_wkhtml_path'),


]
