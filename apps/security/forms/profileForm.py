from django import forms
from django.utils.translation import gettext_lazy as _
from apps.security.models import User


class UserProfileForm(forms.ModelForm):
    """Formulario para actualizar el perfil de usuario"""
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'date_of_birth',
            'avatar',
            'bio',
            'location'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos opcionales más amigables
        for field in self.fields:
            self.fields[field].required = False
            if field != 'avatar':  # Excluimos avatar porque es un FileInput
                self.fields[field].widget.attrs.update({'class': 'form-control'})