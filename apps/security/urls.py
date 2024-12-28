from django.urls import path
from apps.security.views.authenticate import LoginView, RegisterView, ProfileView, LogoutView, ProfileUpdateView

app_name = 'security'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('logout/', LogoutView.as_view(), name='logout')
]
