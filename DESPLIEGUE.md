# Soporte Existencias — cambios para producción y despliegue

Rama `despliegue-seguro`. Prepara la aplicación para publicarse en **https://soporte.maiproject.cl**
(servidor DITEC: Docker + PostgreSQL 17 vía PgBouncer + HAProxy con TLS). No cambia el modelo de
datos ni el diseño de las pantallas.

## 1. Hallazgos de la revisión y qué se hizo

| # | Hallazgo | Riesgo | Cambio |
|---|---|---|---|
| 1 | `SECRET_KEY` escrita en `settings.py` (repositorio **público**) | Crítico: permite falsificar sesiones y tokens | Se lee de la variable `DJANGO_SECRET_KEY`. La clave antigua queda **quemada** (sigue en el historial de Git): no usarla nunca más. |
| 2 | `DEBUG = True` | Alto: muestra código, rutas y configuración ante cualquier error | `DJANGO_DEBUG`, falso por defecto. |
| 3 | Edición de equipos abierta a cualquier técnico escribiendo la URL (el botón solo se veía para administradores) | Alto: control de acceso roto | `editar_equipo` responde **403** si el usuario no es administrador. |
| 4 | Login sin límite de intentos | Alto: fuerza bruta de contraseñas | **django-axes** (MIT): 5 intentos fallidos ⇒ 30 min de bloqueo para ese **usuario + IP** (no la IP sola: toda la red municipal sale por una IP). |
| 5 | Exportaciones Excel/CSV con texto del usuario sin filtrar | Medio: inyección de fórmulas (un nombre `=HYPERLINK(...)` se ejecuta al abrir el archivo) | `celda_segura()` antepone `'` a valores que empiezan con `= + - @`. |
| 6 | Librerías cargadas desde CDN: `unpkg.com/html5-qrcode` **sin versión**, Font Awesome (cdnjs), Google Fonts, logo desde otro sitio | Medio: si el CDN cambia el archivo se ejecuta código ajeno; además filtra la IP de los usuarios a terceros | Todo autoalojado en `frontend/static/vendor/` con versión fija (ver `vendor/LEEME.md`). |
| 7 | Sin cabeceras de seguridad | Medio | Content-Security-Policy estricta (Django 6.1 nativo), cookies `Secure`/`HttpOnly`/`SameSite`, `X-Frame-Options: DENY`, COOP. `onchange` en línea movido a `tabla.js`; `innerHTML` reemplazado por nodos DOM en `form.js`. |
| 8 | Datos inválidos provocaban **error 500** (`int('abc')`, IDs vacíos, N° de serie duplicado al editar, impresora sin campos) | Medio | Validación en el servidor + mensajes al usuario. `form.html` ahora muestra los mensajes (antes no los mostraba). |
| 9 | SQLite | — | `DATABASE_URL` (PostgreSQL por PgBouncer; `CONN_MAX_AGE=0`, sin cursores de servidor). Sin variable ⇒ SQLite local para desarrollo. |
| 10 | Fechas exportadas en UTC, idioma inglés | Bajo | `America/Santiago`, `es-cl`; exportaciones con hora local. |
| 11 | Error de formato en exportación de impresoras (`ws[4]`) y `content_type='text/text/csv'` | Bajo | Corregido (`ws[1]`, `text/csv`). |
| 12 | `requirements.txt` en UTF-16, con paquetes no usados (DRF, Pillow) | Bajo | UTF-8, versiones **y hashes** fijados (`pip-compile --generate-hashes`), sin paquetes sobrantes. Fuente: `requirements.in`. |
| 13 | Enlaces de exportación sin codificar (`?q=` con `&` se rompía) | Bajo | Filtro `urlencode`. |

**Licencias (todo open source):** Django BSD-3 · django-environ MIT · django-jazzmin MIT · django-axes MIT ·
openpyxl MIT · psycopg LGPL-3.0 · WhiteNoise MIT · Gunicorn MIT · sentry-sdk MIT (se usa con GlitchTip, no con
Sentry) · tzdata Apache-2.0 · html5-qrcode Apache-2.0 · Font Awesome Free (CC BY 4.0 / OFL / MIT) · Rubik OFL.
`pip-audit`: sin vulnerabilidades conocidas (28-09-2026).

## 2. Pendiente para el equipo de desarrollo (no se modificó)

1. **La pantalla "Editar" no carga los datos actuales del equipo** (`form.html` no usa `equipo`/`funcionario`):
   al guardar se reemplazan los datos por lo que se escriba. Ahora al menos rechaza nombre/anexo vacíos.
2. `existencias/forms.py` importa `Marca`, que no existe en `catalogos.models`: el archivo no se usa y fallaría
   al importarlo. Recomendación: usar formularios de Django (ModelForm) en todas las vistas en vez de leer
   `request.POST` a mano.
3. Agregar un archivo **LICENSE** al repositorio (hoy es público pero sin licencia = todos los derechos reservados).
4. Los datos son personales (nombres y anexos de funcionarios): considerar la Ley 19.628/21.719 (acceso mínimo,
   tiempo de conservación).
5. `html5-qrcode` no publica versiones desde 2023. A futuro evaluar la API `BarcodeDetector` del navegador o `@zxing/browser` (Apache-2.0).
6. Jazzmin intenta cargar Google Fonts en `/admin/`; la política CSP lo bloquea (el panel usa la fuente del sistema).

## 3. Desarrollo local

```bash
cp .env.example backend/.env       # y poner una DJANGO_SECRET_KEY propia
python -m venv venv && . venv/bin/activate
pip install --require-hashes -r requirements.txt
cd backend && python manage.py migrate && python manage.py runserver
python manage.py test               # pruebas de permisos, validación y exportación
```

Para agregar o subir una dependencia: editar `requirements.in` y ejecutar
`pip-compile --generate-hashes --strip-extras requirements.in`.

## 4. Producción (lo hace el script del servidor)

- Imagen: `Dockerfile` (Python 3.13 slim, usuario sin privilegios UID 10001, Gunicorn, estáticos con WhiteNoise).
- Variables: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`,
  `SENTRY_DSN` (opcional, GlitchTip en errores.maiproject.cl).
- Migraciones: `python manage.py migrate` antes de levantar cada versión nueva.
- `/admin/` solo es accesible desde las IP autorizadas de DITEC (regla en HAProxy).
