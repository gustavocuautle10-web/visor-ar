# -*- coding: utf-8 -*-
"""
app_ar.py — Generador de QR para el visor WebAR (GitHub Pages)
================================================================
Script independiente para el repositorio `visor-ar`. Toma la URL pública
de GitHub Pages (ej. https://tu-usuario.github.io/visor-ar/) y genera un
código QR de alta resolución, con tamaño físico real para impresión en
plano — sin depender de Augment ni de ningún servicio de pago.

Uso por línea de comandos:
    python app_ar.py https://tu-usuario.github.io/visor-ar/ \\
        --salida qr/sitio_001_qr.png --cm 5

    python app_ar.py https://tu-usuario.github.io/visor-ar/ \\
        --modelo sitio_002 --cm 8

El segundo ejemplo agrega el nombre del modelo como parámetro de consulta
(`?modelo=sitio_002`) — útil si en el futuro `index.html` sirve varios
modelos desde el mismo repo y lee ese parámetro con JavaScript para
decidir qué .glb cargar (no implementado aún en el Módulo 1: dilo si lo
quieres y lo agregamos).

Dependencias:
    pip install "qrcode[pil]"
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode, urlparse


DPI = 300  # estándar de impresión


@dataclass
class ResultadoQR:
    ok: bool
    ruta_png: Optional[str] = None
    url_usada: str = ""
    tamano_px: int = 0
    tamano_cm: float = 0.0
    mensaje: str = ""


def _validar_url_github_pages(url: str) -> Optional[str]:
    """
    Verifica que la URL tenga forma de sitio de GitHub Pages válido.
    No hace una petición de red — solo valida el formato, para no
    depender de conexión a internet al generar el QR.
    """
    try:
        p = urlparse(url)
    except Exception:
        return None

    if p.scheme not in ("https", "http"):
        return None
    if not p.netloc:
        return None
    if not p.netloc.endswith("github.io"):
        # No es un error fatal — permite dominios personalizados (CNAME)
        # apuntando al mismo Pages — pero se advierte al usuario.
        return "advertencia_dominio"
    return "ok"


def construir_url(base_url: str, modelo: str = "") -> str:
    """Arma la URL final del QR, agregando ?modelo=... si se indicó."""
    base_url = base_url.rstrip("/") + "/"
    if modelo:
        qs = urlencode({"modelo": modelo})
        return f"{base_url}?{qs}"
    return base_url


def generar_qr(url: str, ruta_salida: str, tamano_cm: float = 5.0) -> ResultadoQR:
    try:
        import qrcode
    except ImportError:
        return ResultadoQR(False, mensaje='Instale con: pip install "qrcode[pil]"')

    estado_url = _validar_url_github_pages(url)
    if estado_url is None:
        return ResultadoQR(False, mensaje=f"URL inválida: {url}")

    advertencia = ""
    if estado_url == "advertencia_dominio":
        advertencia = (
            f"⚠ '{urlparse(url).netloc}' no termina en github.io — "
            "si es un dominio personalizado con CNAME está bien, "
            "si no, verifica la URL."
        )

    # Tamaño físico → píxeles a 300 DPI
    tamano_px = round(tamano_cm / 2.54 * DPI)
    box_size = max(2, tamano_px // 45)  # ~45 módulos de lado en QR típico

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0D1B2A", back_color="white")
        img = img.resize((tamano_px, tamano_px))

        carpeta = os.path.dirname(os.path.abspath(ruta_salida))
        os.makedirs(carpeta, exist_ok=True)
        img.save(ruta_salida, dpi=(DPI, DPI))

        mensaje = f"QR generado: {tamano_cm:.1f}×{tamano_cm:.1f} cm a {DPI} DPI."
        if advertencia:
            mensaje += f"\n{advertencia}"

        return ResultadoQR(
            True, ruta_png=ruta_salida, url_usada=url,
            tamano_px=tamano_px, tamano_cm=tamano_cm, mensaje=mensaje,
        )
    except Exception as ex:
        return ResultadoQR(False, mensaje=f"Error al generar QR: {ex}")


def main():
    ap = argparse.ArgumentParser(
        description="Genera el QR del visor WebAR (GitHub Pages).")
    ap.add_argument("url", help="URL pública de GitHub Pages "
                                 "(ej. https://usuario.github.io/visor-ar/)")
    ap.add_argument("--modelo", default="",
                     help="Nombre del modelo a agregar como ?modelo=... "
                          "(opcional, para repos con varios modelos).")
    ap.add_argument("--salida", default="qr/visor_ar_qr.png",
                     help="Ruta del PNG de salida (default: qr/visor_ar_qr.png).")
    ap.add_argument("--cm", type=float, default=5.0,
                     help="Tamaño físico del QR en cm, para impresión "
                          "en plano (default: 5.0).")
    args = ap.parse_args()

    url_final = construir_url(args.url, args.modelo)
    r = generar_qr(url_final, args.salida, args.cm)

    if r.ok:
        print(f"✅ {r.mensaje}")
        print(f"   Archivo:  {r.ruta_png}")
        print(f"   URL:      {r.url_usada}")
    else:
        print(f"❌ {r.mensaje}")
        sys.exit(1)


if __name__ == "__main__":
    main()
