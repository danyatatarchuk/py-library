from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = (
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    )
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorize",
            "description": 'JWT token. Use format: "Bearer <token>".',
        }
