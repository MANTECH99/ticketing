from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Tes vues personnalisées
    path('dashboard-admin/utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('dashboard-admin/nommer-agent/<int:user_id>/', views.nommer_agent, name='nommer_agent'),
    path('mon-compte/', views.mon_compte, name='mon_compte'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

]
