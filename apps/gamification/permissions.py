from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los propietarios de un objeto
    o miembros del staff modificarlo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Los permisos de lectura se permiten a cualquier usuario autenticado,
        # por lo que siempre permitimos GET, HEAD u OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # El permiso de escritura solo se otorga a:
        # 1. El propietario del objeto
        # 2. Usuarios del staff
        return obj.user == request.user or request.user.is_staff