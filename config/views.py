from django.db import connections
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    summary="Etat de sante de l'API",
    description="Utilise par Docker Compose et la supervision. Route publique.",
    responses={
        200: {"type": "object", "properties": {"status": {"type": "string"},"database": {"type": "string"}}},
        503: {"type": "object","properties": {"status": {"type": "string"},"database": {"type": "string"}}},
    },
    examples=[
        OpenApiExample("Tout va bien", value={"status": "ok", "database": "up"},response_only=True),
    ],
)
@api_view(["GET"])

@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    try:
        with connections["default"].cursor() as curseur:
            curseur.execute("SELECT 1")
        base_ok = True
    except Exception:            
        base_ok = False

    corps = {
        "status": "ok" if base_ok else "degraded",
        "database": "up" if base_ok else "down",
    }

    return Response(corps, status=200 if base_ok else 503)
