from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "status": "Backend is running successfully"
    })


urlpatterns = [
    # Home / health check
    path("", home, name="home"),

    # Django admin
    path("admin/", admin.site.urls),

    # Accounts app URLs
    path("", include("accounts.urls")),
]