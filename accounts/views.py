from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm  # importe le formulaire personnalisé

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Enregistre d'abord les infos supplémentaires
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)  # Connexion automatique
            return redirect('login')  # Redirige vers la liste des événements après inscription
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirection en fonction du rôle
            # Redirection en fonction du rôle
            if user.is_superuser:
                return redirect('dashboard_admin')  # Redirection pour superutilisateurs
            elif user.is_staff:
                return redirect('scan_ticket')  # Redirection pour les agents uniquement
            else:
                return redirect('user_dashboard')  # Redirection pour les utilisateurs standards


    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')



# views.py
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def nommer_agent(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = True
    user.save()
    messages.success(request, f"{user.username} est maintenant agent d’entrée.")
    return redirect('liste_utilisateurs')  # redirige vers ta vue admin


# views.py
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

@user_passes_test(lambda u: u.is_superuser)
def liste_utilisateurs(request):
    users = User.objects.all()
    return render(request, 'accounts/liste_utilisateurs.html', {'users': users})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from events.models import Reservation, Event


@login_required
def mon_compte(request):
    reservations = Reservation.objects.filter(user=request.user).prefetch_related('ticket_set', 'event').order_by('-created_at')
    return render(request, 'accounts/mon_compte.html', {'reservations': reservations})

def user_dashboard(request):
    events = Event.objects.all()
    return render(request, 'events/user_dashboard.html', {'events': events})