"""Premium single-page landscape certificate PDF.

Rendered with a raw reportlab canvas so the layout mirrors the HTML certificate:
gold frames, ribbon, seal, QR and authorized signature block.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from utils.settings_store import get_setting, signature_abs_path


GOLD = HexColor("#c9a227")
GOLD_LIGHT = HexColor("#e8cf76")
GOLD_DARK = HexColor("#8f6918")
INK = HexColor("#1b2338")
MUTED = HexColor("#6b7280")
PRIMARY = HexColor("#0d3b8e")
PAPER = HexColor("#fffdf7")
PAPER_2 = HexColor("#fdf8ec")


def _draw_border(c, w, h, border_color=PRIMARY, gold_color=GOLD):
    c.setStrokeColor(border_color)
    c.setLineWidth(5)
    c.rect(10 * mm, 10 * mm, w - 20 * mm, h - 20 * mm)

    c.setStrokeColor(gold_color)
    c.setLineWidth(3)
    c.rect(14 * mm, 14 * mm, w - 28 * mm, h - 28 * mm)

    c.setLineWidth(1)
    c.setStrokeColor(GOLD_LIGHT)
    c.rect(18 * mm, 18 * mm, w - 36 * mm, h - 36 * mm)

    L = 12 * mm
    c.setStrokeColor(gold_color)
    c.setLineWidth(2.5)
    for x, y, sx, sy in [
        (18 * mm, 18 * mm, 1, 1),
        (w - 18 * mm, 18 * mm, -1, 1),
        (18 * mm, h - 18 * mm, 1, -1),
        (w - 18 * mm, h - 18 * mm, -1, -1),
    ]:
        c.line(x, y, x + sx * L, y)
        c.line(x, y, x, y + sy * L)


def _draw_ribbon(c, w, h, gold_color=GOLD, text="CERTIFICATE OF EXCELLENCE"):
    ribbon_y = h - 36 * mm
    ribbon_w = 105 * mm
    x = (w - ribbon_w) / 2
    c.setFillColor(GOLD_DARK)
    c.rect(x, ribbon_y, ribbon_w, 8 * mm, fill=1, stroke=0)
    c.setFillColor(gold_color)
    c.rect(x + 2, ribbon_y + 1.5, ribbon_w - 4, 5 * mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(INK)
    c.drawCentredString(w / 2, ribbon_y + 2.8 * mm, (text or "")[:60])


def _draw_watermark(c, w, h, text="TYPEMASTER INDIA"):
    c.saveState()
    try:
        c.setFillColor(HexColor("#f3ead0"))
        c.setFont("Helvetica-Bold", 60)
        c.translate(w / 2, h / 2)
        c.rotate(30)
        c.drawCentredString(0, 0, (text or "")[:40])
    finally:
        c.restoreState()


def _centered(c, text, y, font, size, color):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(c._pagesize[0] / 2, y, text)


def _stat_grid(c, w, y, items):
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


def _draw_seal(c, w, h, gold_color=GOLD):
    seal_x = w - 44 * mm
    seal_y = h - 76 * mm
    c.setFillColor(HexColor("#f7e08a"))
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(2)
    c.circle(seal_x, seal_y, 15 * mm, fill=1, stroke=1)
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(1)
    c.circle(seal_x, seal_y, 11 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(GOLD_DARK)
    c.drawCentredString(seal_x, seal_y + 3 * mm, "EXCELLENCE")
    c.drawCentredString(seal_x, seal_y - 0.5 * mm, "IN")
    c.drawCentredString(seal_x, seal_y - 4 * mm, "TYPING")


def _hex_or(default, value):
    """Return a reportlab HexColor from a #rrggbb string, else the default."""
    try:
        if value and isinstance(value, str) and value.startswith("#") and len(value) in (4, 7):
            return HexColor(value)
    except Exception:
        pass
    return default


def create_certificate(path, result, certificate_id, user, verify_url=None):
    w, h = landscape(A4)
    c = canvas.Canvas(path, pagesize=landscape(A4))
    c._pagesize = (w, h)

    # Certificate designer settings (mirrors the HTML certificate).
    border_color = _hex_or(PRIMARY, get_setting("cert_border_color"))
    gold_color = _hex_or(GOLD, get_setting("cert_gold_color"))
    show_ribbon = get_setting("cert_ribbon_enabled", True)
    ribbon_text = get_setting("cert_ribbon_text", "CERTIFICATE OF EXCELLENCE")
    show_seal = get_setting("cert_seal_enabled", True)
    show_watermark = get_setting("cert_watermark_enabled", True)
    watermark_text = get_setting("cert_watermark_text", "TYPEMASTER INDIA")
    title_text = get_setting("cert_title", "Certificate of Achievement")
    subtitle_text = get_setting("cert_subtitle", "Official Typing Performance Record")

    c.setFillColor(PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(PAPER_2)
    c.rect(w * 0.55, 0, w * 0.45, h, fill=1, stroke=0)
    c.setFillColor(PAPER)
    c.rect(0, 0, w * 0.55, h, fill=1, stroke=0)

    _draw_border(c, w, h, border_color, gold_color)
    if show_ribbon:
        _draw_ribbon(c, w, h, gold_color, ribbon_text)
    if show_seal:
        _draw_seal(c, w, h, gold_color)
    if show_watermark:
        _draw_watermark(c, w, h, watermark_text)

    org = get_setting("org_name", "TypeMaster India")
    founder = get_setting("founder_name", "Sumit Goswami")
    founder_title = get_setting("founder_title", "Founder")
    footer_note = get_setting("certificate_footer", "Digitally generated and verifiable online.")

    _centered(c, org.upper(), h - 48 * mm, "Helvetica-Bold", 9, MUTED)
    _centered(c, title_text, h - 58 * mm, "Times-Bold", 26, border_color)
    _centered(c, subtitle_text, h - 66 * mm, "Helvetica", 11, GOLD_DARK)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(w / 2 - 42 * mm, h - 70 * mm, w / 2 + 42 * mm, h - 70 * mm)
    _centered(c, "This is to certify that", h - 78 * mm, "Helvetica-Oblique", 11, MUTED)

    # Name in the brand/border colour to mirror the HTML certificate.
    _centered(c, user.full_name, h - 92 * mm, "Times-BoldItalic", 28, border_color)
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(1)
    c.line(w / 2 - 52 * mm, h - 96 * mm, w / 2 + 52 * mm, h - 96 * mm)

    _centered(
        c,
        f"has successfully completed the {org} Typing Test with outstanding performance.",
        h - 104 * mm,
        "Helvetica",
        10.5,
        INK,
    )

    stats = [
        ("Gross WPM", result.gross_wpm),
        ("Net WPM", result.net_wpm),
        ("CPM", result.cpm),
        ("Accuracy", f"{result.accuracy}%"),
        ("Errors", result.errors),
    ]
    # Pushed lower to fill the page evenly (mirrors HTML vertical rhythm).
    _stat_grid(c, w, h - 138 * mm, stats)

    meta = (
        f"Language: {result.language}    |    Difficulty: {result.difficulty}    |    "
        f"Duration: {result.duration}s    |    Layout: QWERTY"
    )
    _centered(c, meta, h - 148 * mm, "Helvetica", 9.5, MUTED)

    footer_y = 24 * mm
    right_x = w - 24 * mm

    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(24 * mm, footer_y + 9 * mm, "CERTIFICATE NO.")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(24 * mm, footer_y + 4 * mm, certificate_id)

    issue_date = result.created_at.strftime("%d %B %Y") if result.created_at else datetime.now().strftime("%d %B %Y")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(24 * mm, footer_y - 3 * mm, "DATE OF ISSUE")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(24 * mm, footer_y - 8 * mm, issue_date)

    if verify_url:
        qr_size = 26 * mm
        _draw_qr(c, verify_url, w / 2 - qr_size / 2, footer_y - 8 * mm, qr_size)
        c.setFont("Helvetica", 7)
        c.setFillColor(MUTED)
        c.drawCentredString(w / 2, footer_y - 12 * mm, "Scan to Verify Authenticity")

    sig_path = signature_abs_path()
    if sig_path and os.path.exists(sig_path):
        sig_w, sig_h = 45 * mm, 14 * mm
        c.drawImage(
            sig_path,
            right_x - sig_w,
            footer_y - 1 * mm,
            width=sig_w,
            height=sig_h,
            preserveAspectRatio=True,
            mask="auto",
        )
        text_y = footer_y - 8 * mm
    else:
        c.setFont("Helvetica", 8)
        c.setFillColor(GOLD_DARK)
        c.drawRightString(right_x, footer_y + 6 * mm, "FOUNDER")
        text_y = footer_y

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(INK)
    c.drawRightString(right_x, text_y, founder)
    c.drawRightString(right_x, text_y - 5 * mm, founder_title)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(right_x, text_y - 10 * mm, org)

    note = footer_note
    if verify_url and "Verify" not in note:
        note = f"{footer_note} Verify at {verify_url}"
    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(w / 2, 16 * mm, note)

    c.showPage()
    c.save()
