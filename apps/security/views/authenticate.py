from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, View
from django.utils.translation import gettext_lazy as _
from torch import layout
from apps.security.forms.auth import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from apps.security.forms.profileForm import UserProfileForm
from apps.security.models import User

class LoginView(View):
    template_name = 'security/auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            user.increment_login_count(request.META.get('REMOTE_ADDR'))
            messages.success(request, _('¡Bienvenido de nuevo!'))
            return redirect('home')
        else:
            messages.error(request, _('Correo electrónico o contraseña incorrectos'))
            return render(request, self.template_name)

class RegisterView(View):
    template_name = 'security/auth/register.html'
    form_class = UserRegistrationForm
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('¡Cuenta creada exitosamente!'))
            return redirect('home')
        return render(request, self.template_name, {'form': form})
    
class ProfileView(LoginRequiredMixin, DetailView):
    """
    View for displaying user profile information.
    """
    model = User
    template_name = 'security/auth/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        """
        Get the user profile to display. If a username is provided in the URL,
        show that user's profile (if public). Otherwise, show the current user's profile.
        """
        if self.kwargs.get('username'):
            user = self.model.objects.filter(username=self.kwargs['username']).first()
            if user and user.privacy_settings.get('public_profile', False):
                return user
            raise Http404(_("Profile not found or is private"))
        return self.request.user

    def get_context_data(self, **kwargs):
        """Add additional context data for the template."""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Add impact metrics and other relevant data
        context.update({
            'impact_metrics': user.get_impact_metrics(),
            'total_points': user.get_total_points(),
            'active_badges': user.get_active_badges(),
            'is_own_profile': user == self.request.user,
        })
        
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar el perfil de usuario"""
    model = User
    form_class = UserProfileForm
    template_name = 'security/auth/profile_edit.html'
    success_url = reverse_lazy('security:profile')
    
    def get_object(self, queryset=None):
        """Retorna el usuario actual"""
        return self.request.user
    
    def form_valid(self, form):
        """Si el formulario es válido, guarda los cambios y muestra un mensaje"""
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Si el formulario es inválido, muestra un mensaje de error"""
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Actualizar Perfil'
        context['user_points'] = self.request.user.get_total_points()
        context['active_badges'] = self.request.user.get_active_badges()
        return context
    
class LogoutView(View):
    def post(self, request):
        logout(request)  # Termina la sesión del usuario
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return redirect('security:login')