"""Premium single-page landscape certificate PDF.

Rendered with a raw reportlab canvas (not platypus) so the layout, golden
border, seal, QR and signature block mirror the HTML certificate exactly:
one A4 landscape page, no clipping, no overflow.
"""

from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


# Palette (matches certificate.css)
GOLD = HexColor("#c9a227")
GOLD_LIGHT = HexColor("#e8cf76")
INK = HexColor("#1b2338")
MUTED = HexColor("#6b7280")
PRIMARY = HexColor("#2f6bff")
PAPER = HexColor("#fffdf7")


def _draw_border(c, w, h):
    # Outer thick gold frame
    c.setStrokeColor(GOLD)
    c.setLineWidth(4)
    c.rect(12 * mm, 12 * mm, w - 24 * mm, h - 24 * mm)

    # Inner thin gold frame
    c.setLineWidth(1)
    c.setStrokeColor(GOLD_LIGHT)
    c.rect(16 * mm, 16 * mm, w - 32 * mm, h - 32 * mm)

    # Corner accents
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    L = 14 * mm
    corners = [
        (16 * mm, 16 * mm, 1, 1),
        (w - 16 * mm, 16 * mm, -1, 1),
        (16 * mm, h - 16 * mm, 1, -1),
        (w - 16 * mm, h - 16 * mm, -1, -1),
    ]
    for x, y, sx, sy in corners:
        c.line(x, y, x + sx * L, y)
        c.line(x, y, x, y + sy * L)


def _centered(c, text, y, font, size, color):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(c._pagesize[0] / 2, y, text)


def _stat_grid(c, w, y, items):
    """Draw an evenly spaced row of stat boxes centered on the page."""
    n = len(items)
    box_w = 42 * mm
    gap = 6 * mm
    total = n * box_w + (n - 1) * gap
    start_x = (w - total) / 2

    for i, (label, value) in enumerate(items):
        x = start_x + i * (box_w + gap)

        c.setFillColor(HexColor("#fbf6e6"))
        c.setStrokeColor(GOLD_LIGHT)
        c.setLineWidth(1)
        c.roundRect(x, y, box_w, 20 * mm, 4, fill=1, stroke=1)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(PRIMARY)
        c.drawCentredString(x + box_w / 2, y + 11 * mm, str(value))

        c.setFont("Helvetica", 7.5)
        c.setFillColor(MUTED)
        c.drawCentredString(x + box_w / 2, y + 4.5 * mm, label.upper())


def _draw_qr(c, data, x, y, size):
    widget = QrCodeWidget(data)
    bounds = widget.getBounds()
    bw = bounds[2] - bounds[0]
    bh = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size / bw, 0, 0, size / bh, 0, 0])
    d.add(widget)
    renderPDF.draw(d, c, x, y)


def create_certificate(path, result, certificate_id, user, verify_url=None):

    w, h = landscape(A4)

    c = canvas.Canvas(path, pagesize=landscape(A4))
    c._pagesize = (w, h)

    # Background
    c.setFillColor(PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    _draw_border(c, w, h)

    # ---------------- Header ----------------
    _centered(c, "TypeMaster India", h - 34 * mm, "Times-Bold", 30, INK)
    _centered(c, "CERTIFICATE OF ACHIEVEMENT", h - 46 * mm, "Helvetica-Bold", 15, GOLD)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(w / 2 - 40 * mm, h - 50 * mm, w / 2 + 40 * mm, h - 50 * mm)

    _centered(c, "This is to certify that", h - 62 * mm, "Helvetica-Oblique", 12, MUTED)

    # ---------------- Name ----------------
    _centered(c, user.full_name, h - 78 * mm, "Times-BoldItalic", 30, INK)
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(1)
    c.line(w / 2 - 55 * mm, h - 82 * mm, w / 2 + 55 * mm, h - 82 * mm)

    _centered(
        c,
        "has successfully completed the TypeMaster India Typing Test with",
        h - 92 * mm,
        "Helvetica",
        11,
        INK,
    )
    _centered(
        c,
        "outstanding typing performance and dedication.",
        h - 98 * mm,
        "Helvetica",
        11,
        INK,
    )

    # ---------------- Stats ----------------
    stats = [
        ("Gross WPM", result.gross_wpm),
        ("Net WPM", result.net_wpm),
        ("CPM", result.cpm),
        ("Accuracy", f"{result.accuracy}%"),
        ("Errors", result.errors),
    ]
    _stat_grid(c, w, h - 122 * mm, stats)

    # Meta line (language / difficulty / duration / layout)
    meta = (
        f"Language: {result.language}    |    "
        f"Difficulty: {result.difficulty}    |    "
        f"Duration: {result.duration}s    |    Layout: QWERTY"
    )
    _centered(c, meta, h - 130 * mm, "Helvetica", 10, MUTED)

    # ---------------- Footer ----------------
    footer_y = 26 * mm

    # Left: certificate id + issue date
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(24 * mm, footer_y + 9 * mm, "CERTIFICATE ID")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(24 * mm, footer_y + 4 * mm, certificate_id)

    issue_date = result.created_at.strftime("%d %B %Y") if result.created_at else datetime.now().strftime("%d %B %Y")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(24 * mm, footer_y - 3 * mm, "ISSUED ON")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(24 * mm, footer_y - 8 * mm, issue_date)

    # Center: QR code
    if verify_url:
        qr_size = 26 * mm
        _draw_qr(c, verify_url, w / 2 - qr_size / 2, footer_y - 8 * mm, qr_size)
        c.setFont("Helvetica", 7)
        c.setFillColor(MUTED)
        c.drawCentredString(w / 2, footer_y - 12 * mm, "Scan to Verify")

    # Right: signature + seal
    right_x = w - 24 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    c.line(right_x - 45 * mm, footer_y + 3 * mm, right_x, footer_y + 3 * mm)
    c.setFont("Times-BoldItalic", 13)
    c.setFillColor(INK)
    c.drawRightString(right_x, footer_y + 5 * mm, "Sumit Goswami")
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(right_x, footer_y - 2 * mm, "Founder - TypeMaster India")

    # Seal (top-right circular badge)
    seal_x = w - 42 * mm
    seal_y = h - 78 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.setFillColor(HexColor("#fbf2d0"))
    c.circle(seal_x, seal_y, 15 * mm, fill=1, stroke=1)
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(1)
    c.circle(seal_x, seal_y, 11 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(GOLD)
    c.drawCentredString(seal_x, seal_y + 3 * mm, "EXCELLENCE")
    c.drawCentredString(seal_x, seal_y - 1 * mm, "IN")
    c.drawCentredString(seal_x, seal_y - 5 * mm, "TYPING")

    # Security note
    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(MUTED)
    note = "This certificate is digitally generated and verifiable online."
    if verify_url:
        note = f"Digitally generated. Verify at {verify_url}"
    c.drawCentredString(w / 2, 18 * mm, note)

    c.showPage()
    c.save()
