"""
Configuration de l’administration Django pour le modèle utilisateur.
Définit l’affichage, les filtres et les champs relatifs aux consentements
RGPD dans l’interface d’administration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Affichage personnalisé du modèle User dans l’administration."""

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Informations personnelles"),
            {"fields": ("first_name", "last_name", "email", "age")},
        ),
        (
            _("Consentements et paramètres RGPD"),
            {"fields": ("can_be_contacted", "can_data_be_shared")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Dates importantes"),
            {"fields": ("last_login", "date_joined", "created_time")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "age",
                    "can_be_contacted",
                    "can_data_be_shared",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "age",
        "is_staff",
        "can_be_contacted",
        "can_data_be_shared",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "can_be_contacted",
        "can_data_be_shared",
    )
    search_fields = ("username", "email")
    ordering = ("username",)
