"""
Configuración de Django para Soporte Existencias.

Todo lo que cambia entre el computador del desarrollador y el servidor se lee desde
variables de entorno (o desde backend/.env en desarrollo). Ver .env.example.
Nunca escribir claves ni contraseñas en este archivo: el repositorio es público.
"""

from datetime import timedelta
from pathlib import Path

import environ
from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

env = environ.Env()
# En desarrollo se puede usar backend/.env (está en .gitignore). En el servidor las
# variables llegan desde Docker y este archivo no existe.
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

# --- Núcleo ------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=False)
# Sin valor por defecto: si falta, Django no arranca (mejor que usar una clave conocida).
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",  # bloqueo de fuerza bruta en el login
    "usuarios",
    "existencias",
    "catalogos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # archivos estáticos sin servidor extra
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "config.seguridad.CSPAdminMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",  # debe ir al final
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # debe ir primero
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_ROOT / "frontend" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de datos -----------------------------------------------------------
# Servidor: DATABASE_URL=postgres://usuario:clave@maipu-pgbouncer:6432/soporte
# Desarrollo: si no se define, se usa SQLite local.
DATABASES = {
    "default": env.db_url("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    # PgBouncer en modo transacción: sin conexiones persistentes ni cursores del lado servidor.
    DATABASES["default"]["CONN_MAX_AGE"] = 0
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
    DATABASES["default"].setdefault("OPTIONS", {})["connect_timeout"] = 5

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # igual que las migraciones existentes

# --- Contraseñas ---------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "usuarios.Tecnico"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"

# --- Idioma y hora -------------------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos --------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [PROJECT_ROOT / "frontend" / "static"]
STATIC_ROOT = env.path("DJANGO_STATIC_ROOT", default=PROJECT_ROOT / "staticfiles")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# Jazzmin referencia una carpeta ('vendor/bootswatch') que no está en el manifiesto:
# sin esto, /admin/ responde error 500.
WHITENOISE_MANIFEST_STRICT = False
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"

# --- Correo --------------------------------------------------------------------
# Aún no hay servidor de correo: en producción se descartan (no se muestran en consola).
MAILERS = {
    "default": {
        "BACKEND": env.str(
            "DJANGO_EMAIL_BACKEND",
            default="django.core.mail.backends.console.EmailBackend" if DEBUG
            else "django.core.mail.backends.dummy.EmailBackend",
        ),
    },
}
SILENCED_SYSTEM_CHECKS = ["mail.E001"]  # quitar cuando exista SMTP

# --- Seguridad HTTP ------------------------------------------------------------
# Detrás de HAProxy: TLS termina en el proxy, que envía X-Forwarded-Proto y X-Real-IP.
DETRAS_DE_PROXY = env.bool("DJANGO_DETRAS_DE_PROXY", default=not DEBUG)
if DETRAS_DE_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 9          # una jornada laboral
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# HTTPS y HSTS los aplica HAProxy (redirección 301 + Strict-Transport-Security).
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SILENCED_SYSTEM_CHECKS += ["security.W004", "security.W008"]

# Content-Security-Policy: todo se sirve desde el propio sitio (sin CDN).
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF],
    "style-src-attr": [CSP.UNSAFE_INLINE],  # atributos style="" en las plantillas
    "img-src": [CSP.SELF, "data:", "blob:"],
    "font-src": [CSP.SELF],
    "connect-src": [CSP.SELF],
    "media-src": [CSP.SELF, "blob:"],       # cámara del lector de códigos de barra
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
}

# --- Protección contra fuerza bruta (django-axes) -----------------------------------
# Toda la red municipal sale por una sola IP pública: se bloquea la combinación
# usuario + IP (no la IP sola), para no dejar sin servicio a toda la oficina.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "bloqueado.html"
AXES_CLIENT_IP_CALLABLE = "config.seguridad.ip_cliente"

# --- Registro (a la salida estándar: lo recoge Docker y se ve en Dozzle) ---------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"consola": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["consola"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["consola"], "level": env.str("DJANGO_LOG_LEVEL", default="INFO"), "propagate": False},
        "axes": {"handlers": ["consola"], "level": "WARNING", "propagate": False},
    },
}

# --- Errores a GlitchTip (opcional; compatible con el SDK de Sentry) -----------------
SENTRY_DSN = env.str("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env.str("SENTRY_ENVIRONMENT", default="produccion"),
        send_default_pii=False,  # no enviar datos personales de los funcionarios
        traces_sample_rate=0.0,
    )

JAZZMIN_SETTINGS = {
    "site_title": "Soporte Existencias",
    "site_header": "Soporte Existencias",
    "site_brand": "Soporte Existencias",
    "site_logo": None,
    "welcome_sign": "Bienvenido a Soporte Existencias",
}
