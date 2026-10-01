# Soporte Existencias — despliegue seguro (versión 2)

Rama `despliegue-seguro-v2`, construida **sobre el `main` actual** (commit `5aad927`, con marca/modelo y
N° de inventario escaneables). Conserva todas las funciones nuevas del equipo y vuelve a aplicar lo
necesario para publicar en **https://soporte.maiproject.cl**.

## 0. Lo más importante para el equipo

- **`python manage.py runserver` funciona sin configurar nada.** Por defecto la app arranca en modo
  *desarrollo*: DEBUG activo, SQLite, clave temporal y la política CSP solo **avisa** en la consola del
  navegador (no bloquea). El modo *producción* lo activa el `Dockerfile` (`DJANGO_ENTORNO=produccion`).
  En la versión 1, sin un `.env` la app no arrancaba; probablemente por eso se revirtió.
- **No modificar migraciones ya aplicadas.** El commit `fa39ff6` cambió `0001`/`0002` y borró
  `0003_registro_tables`. La base del servidor ya tenía esas migraciones aplicadas y no se puede
  actualizar en el lugar. Para cambiar un modelo: editar `models.py` y ejecutar `python manage.py
  makemigrations`, que crea una migración **nueva** (`0004_...`). El script de despliegue detecta este caso.
- **Para agregar una librería de JavaScript o CSS**, se descarga a `frontend/static/` con versión fija
  (ver `frontend/static/vendor/LEEME.md`), no desde un CDN.
- **Para agregar un paquete Python**, se edita `requirements.in` y se ejecuta
  `pip-compile --generate-hashes --strip-extras requirements.in`.

## 1. Cambios de esta versión

| # | Tema | Antes | Ahora |
|---|---|---|---|
| 1 | Clave secreta de Django | Escrita en `settings.py`, en un repositorio público | Variable `DJANGO_SECRET_KEY`, obligatoria en producción. La clave antigua está **quemada** |
| 2 | DEBUG y base de datos | DEBUG fijo y SQLite | Por entorno; en producción usa PostgreSQL por PgBouncer (`DATABASE_URL`) |
| 3 | Login | Sin límite de intentos | django-axes: 5 intentos fallidos bloquean 30 min la combinación usuario + IP |
| 4 | Cabeceras de seguridad | Ninguna | CSP nativa de Django 6.1, cookies seguras, `X-Frame-Options: DENY`, COOP |
| 5 | Recursos externos | Google Fonts, Font Awesome (cdnjs) y logo desde otro sitio | Autoalojados con versión fija |
| 6 | **Lector de códigos** | Las plantillas cargaban `js/html5-qrcode.min.js`, pero el archivo **no estaba en el repositorio** (404: sin lector) | Agregado `frontend/static/js/html5-qrcode.min.js` (v2.3.8, Apache-2.0) |
| 7 | **Cámara en notebooks** | `cameras.id` (siempre undefined): sin cámara trasera, el lector fallaba | Usa la cámara trasera si existe; si no, la disponible |
| 8 | **Excel de impresoras** | `for cell in ws:` recorría filas, no celdas: **error 500 siempre** | Encabezados en `ws[1]` |
| 9 | CSV | `charset=utf-8-sig` repetía el BOM al inicio de **cada fila** | BOM una sola vez |
| 10 | Fórmulas en exportaciones | Un nombre como `=HYPERLINK(...)` se ejecutaba al abrir Excel | Se guarda como texto (`celda_segura`) |
| 11 | Datos manipulados | `cantidad_monitores="abc"` o IDs no numéricos daban error 500; `cantidad_monitores=100000` recorría un bucle enorme; impresora sin Estado daba error 500 | Mensaje al usuario; monitores acotados a 2 |
| 12 | Fechas en exportaciones | En UTC | Hora de Chile |
| 13 | JavaScript en línea | `onchange="this.form.submit()"` (incompatible con CSP); `innerHTML` con mensajes en el lector | `tabla.js` y nodos DOM |
| 14 | Dependencias | Sin hashes; DRF, Pillow y psycopg2-binary sin uso | `requirements.txt` con versión **y hash**; psycopg 3; sin paquetes sobrantes |
| 15 | Ejecución | — | `Dockerfile`: Python 3.13 slim, usuario sin privilegios (UID 10001), Gunicorn y WhiteNoise |
| 16 | Pruebas | Vacías | 13 pruebas: permisos, datos inválidos, exportaciones y fórmulas |

`pip-audit`: sin vulnerabilidades conocidas. Todas las dependencias son open source (BSD, MIT, LGPL, Apache).

## 2. Pendiente para el equipo (no se modificó)

1. `existencias/forms.py` importa `Marca` y `TipoImpresora`, que ya no existen en `catalogos`. El
   archivo no se usa, y si alguien lo importa la app falla. Corregirlo o eliminarlo.
2. `tabla.html` no muestra los mensajes de éxito ("Equipo registrado correctamente").
3. El repositorio sigue sin archivo **LICENSE**.
4. El panel `/admin/` (Jazzmin) intenta cargar Google Fonts; la CSP lo bloquea y no afecta el uso.

## 3. Desarrollo local

```bash
python -m venv venv && . venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd backend && python manage.py migrate && python manage.py runserver
python manage.py test                               # 13 pruebas
```
