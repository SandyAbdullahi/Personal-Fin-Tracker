# core/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.auth_views import FlexibleTokenObtainPairView
from core.views_health import health

urlpatterns = [
    path("admin/", admin.site.urls),
    # 🔑 machine-readable schema
    # ─── docs ───────────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI → nice for developers
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc → static, minimalist reference
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/finance/", include("finance.urls")),
    path("healthz/", health, name="health"),
    # ✅ SimpleJWT
    path("api/token/", FlexibleTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
