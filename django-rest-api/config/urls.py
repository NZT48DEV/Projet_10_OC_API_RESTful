from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/", include("projects.urls")),
    path("api-auth/", include("api_auth.urls")),
    path("", lambda request: redirect("/api-auth/")),
]
