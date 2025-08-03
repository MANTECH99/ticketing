from django.urls import path
from . import views

urlpatterns = [
    path('valider-ticket/<int:ticket_id>/', views.valider_ticket, name='valider_ticket'),
    path('event/<int:event_id>/a-valider/', views.tickets_a_valider, name='tickets_a_valider'),
    path('event', views.tickets_a_valider, name='liste_ticket'),
    path('events/validation/', views.events_pour_validation, name='events_pour_validation'),
    path('ticket/<int:ticket_id>/valider/', views.valider_manuellement, name='valider_manuellement'),

]
