# core/views_health.py
from django.http import JsonResponse


def health(request):
    """
    Lightweight liveness probe.
    Render pings /healthz by default; other clouds do the same.
    """
    return JsonResponse({"status": "ok"})
