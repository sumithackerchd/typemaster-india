"""Certificate identity + QR helpers.

Every result gets a unique, persistent certificate id and verification token
the first time its certificate is viewed/downloaded. The QR code encodes the
public verification URL (``/verify/<certificate_id>``) so scanning it always
opens the verification page for that exact certificate.
"""

import base64
import secrets
from datetime import datetime

import qrcode
import qrcode.image.svg

from models import db


def generate_certificate_id(result_id):
    """Deterministic, human-readable id (unique per result)."""
    today = datetime.now().strftime("%Y%m%d")
    return f"TMI-{today}-{result_id:06d}"


def ensure_certificate_identity(result_data):
    """Attach a unique certificate id + verification token to a result.

    Runs once per result: on first call the values are generated and stored;
    subsequent calls reuse the stored values so a certificate's QR/token never
    changes for that result — but every *different* result gets its own.
    """
    changed = False

    if not result_data.certificate_id:
        result_data.certificate_id = generate_certificate_id(result_data.id)
        changed = True

    if not result_data.verify_token:
        # 32 hex chars — unguessable, never reused across certificates.
        result_data.verify_token = secrets.token_hex(16)
        changed = True

    if changed:
        db.session.commit()

    return result_data.certificate_id, result_data.verify_token


def verification_url(base_url, certificate_id):
    """Absolute URL the QR code should point to."""
    return f"{base_url.rstrip('/')}/verify/{certificate_id}"


def build_qr_svg_data_uri(data):
    """Return a QR code for ``data`` as an SVG ``data:`` URI (no PIL needed)."""
    img = qrcode.make(
        data,
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=10,
        border=2,
    )

    from io import BytesIO

    buffer = BytesIO()
    img.save(buffer)
    svg_bytes = buffer.getvalue()

    encoded = base64.b64encode(svg_bytes).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_qr_png_bytes(data):
    """Return QR code PNG bytes (used by the PDF generator via reportlab)."""
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.get_matrix()
