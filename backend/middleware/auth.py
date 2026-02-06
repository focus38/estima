from fastapi import Request, status
from fastapi.security import HTTPBasic
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

from starlette.responses import Response

from backend import config


security = HTTPBasic()

class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Исключаем статику и публичные эндпоинты из проверки
        if request.url.path.startswith("/static/css") or \
                request.url.path.startswith("/static/js") or \
                request.url.path.startswith("/static/image") or \
                request.url.path.startswith("/docs") or \
                request.url.path.startswith("/openapi.json") or \
                request.url.path.startswith("/redoc") or \
                request.url.path.startswith("/favicon.ico"):
            return await call_next(request)

        # Проверяем заголовок Authorization
        authorization = request.headers.get("Authorization")

        if not authorization:
            return self._create_unauthorized_response()

        try:
            scheme, credentials = authorization.split()
            if scheme.lower() != "basic":
                return self._create_unauthorized_response()

            import base64
            decoded = base64.b64decode(credentials).decode("ascii")
            username, password = decoded.split(":")

            if username not in config.USERS:
                return self._create_unauthorized_response()

            correct_password = secrets.compare_digest(
                password.encode('utf-8'),
                config.USERS[username].encode('utf-8')
            )

            if not correct_password:
                return self._create_unauthorized_response()

        except Exception:
            return self._create_unauthorized_response()

        response = await call_next(request)
        return response

    @staticmethod
    def _create_unauthorized_response():
        response = Response(status_code=status.HTTP_401_UNAUTHORIZED)
        response.headers["WWW-Authenticate"] = 'Basic realm="Authentication required"'
        return response