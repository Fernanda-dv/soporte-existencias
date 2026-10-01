# Imagen de producción de Soporte Existencias (Django 6.1 + Gunicorn).
# Todo open source: Python (PSF), Debian, Django (BSD), Gunicorn (MIT), WhiteNoise (MIT)...
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias con versión Y hash fijados: si un paquete de PyPI cambia, la construcción falla.
COPY requirements.txt .
RUN pip install --require-hashes -r requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/

# Archivos estáticos listos en la imagen (la clave de construcción no se usa al ejecutar).
RUN DJANGO_ENTORNO=produccion \
    DJANGO_SECRET_KEY=solo-para-construir-la-imagen \
    DATABASE_URL=sqlite:////tmp/construccion.sqlite3 \
    DJANGO_STATIC_ROOT=/app/staticfiles \
    python backend/manage.py collectstatic --noinput -v0

# Nunca correr como root
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER 10001:10001

WORKDIR /app/backend
# La imagen SIEMPRE arranca en modo producción (exige clave y base de datos por variables).
ENV DJANGO_ENTORNO=produccion \
    DJANGO_STATIC_ROOT=/app/staticfiles
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4).status == 200 else 1)"

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--max-requests", "1000", "--max-requests-jitter", "100", \
     "--worker-tmp-dir", "/tmp", \
     "--no-control-socket", \
     "--access-logfile", "-"]
