# visor-ar

Visor de Realidad Aumentada 100% gratuito y sin servidores de pago, basado
en [`<model-viewer>`](https://modelviewer.dev) (Google, Apache-2.0) y
[GitHub Pages](https://pages.github.com). Solo Android (Google Scene
Viewer + WebXR como respaldo en navegador).

## Requisito del dispositivo que va a escanear el QR

- Android con **ARCore** instalado (la gran mayoría de equipos desde ~2018).
  Google Play instala/actualiza ARCore automáticamente en dispositivos
  compatibles — no requiere que el usuario haga nada extra.
- No requiere la app Augment, ni ninguna app de terceros: el propio
  navegador (Chrome) activa la cámara AR nativa del sistema.

## 1. Publicar el sitio (una sola vez)

1. Sube esta carpeta a un repositorio de GitHub llamado, por ejemplo, `visor-ar`.
2. En el repo: **Settings → Pages → Source → Deploy from branch**,
   selecciona la rama `main` y carpeta `/ (root)`.
3. GitHub te da la URL pública, algo como:
   `https://tu-usuario.github.io/visor-ar/`
4. Guárdala — es la que usarás en todos los QR (`app_ar.py`).

## 2. Flujo manual para publicar un modelo nuevo

Por ahora estos pasos son manuales (no están conectados automáticamente,
a propósito — ver nota al final):

```
① Motor Sísmico (sitio/visor3d/)
   converter.py        → convierte .ifc / .png / .jpg a modelo.glb
   optimizar_glb.py     → modelo.glb → modelo_opt.glb (texturas livianas)

② Copiar el resultado a este repo
   cp modelo_opt.glb  visor-ar/models/sitio_001.glb

③ Subir el cambio a GitHub
   git add models/sitio_001.glb
   git commit -m "Agrega modelo sitio_001"
   git push

④ Generar el QR (en este repo, visor-ar/)
   python app_ar.py https://tu-usuario.github.io/visor-ar/ \
       --modelo sitio_001 --salida qr/sitio_001_qr.png --cm 5
```

El QR resultante apunta a:
`https://tu-usuario.github.io/visor-ar/?modelo=sitio_001`

`index.html` lee ese `?modelo=` y carga `models/sitio_001.glb`
automáticamente — así un mismo sitio puede servir varios modelos, cada
uno con su propio QR.

## 3. Varios modelos en el mismo repo

Repite el paso 2 con distintos nombres (`sitio_002`, `sitio_003`, …) —
cada `.glb` en `models/` con su propio QR generado con `--modelo`.

## Solución de problemas

| Síntoma | Causa probable |
|---|---|
| El botón "Ver en Realidad Aumentada" no aparece | El dispositivo no tiene ARCore, o no es Android. |
| Se abre el modelo en 3D pero no entra a AR | Falta actualizar Google Play Services for AR (Chrome suele pedirlo solo). |
| "No se pudo cargar sitio_XXX.glb" en la barra superior | El `.glb` no está en `models/` con ese nombre exacto, o no se hizo `git push`. |
| El QR funciona en algunos celulares y en otros no | Normal — depende de si el equipo tiene ARCore certificado por Google. |

## Nota sobre la automatización

Los tres scripts (`converter.py` → `optimizar_glb.py` → `app_ar.py`)
están hechos para poder encadenarse en un solo flujo desde
`tab_sitio.py` (botón único), pero por decisión del proyecto, por ahora
se corren por separado, a mano. Cuando se quiera automatizar, ese es el
siguiente paso natural.
