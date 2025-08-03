from django.urls import path
from . import views

urlpatterns = [
    path('telecharger/<int:ticket_id>/', views.telecharger_ticket, name='telecharger_ticket'),
]
