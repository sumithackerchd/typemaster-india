"""Premium single-page landscape certificate PDF.

Rendered with a raw reportlab canvas so the layout mirrors the HTML certificate
1:1: the same gold/blue frame, top tricolour strip, gold ribbon, crown medallion,
embossed seal, watermark, stat grid, QR and authorized-signature block.

The exact same TrueType fonts used by the web certificate (Cinzel for headings,
Cormorant Garamond for body copy) are embedded here, so the downloaded PDF and
the on-screen certificate are visually identical.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from utils.settings_store import get_setting, signature_abs_path


GOLD = HexColor("#c9a227")
GOLD_LIGHT = HexColor("#f7e08a")
GOLD_MID = HexColor("#d4af37")
GOLD_DARK = HexColor("#8f6918")
INK = HexColor("#1b2338")
MUTED = HexColor("#6b7280")
PRIMARY = HexColor("#0d3b8e")
PAPER = HexColor("#fffef9")
PAPER_2 = HexColor("#fdf8ec")
WATERMARK_BLUE = HexColor("#eef2fb")


# ---------------------------------------------------------------------------
# Fonts — embed the same typefaces the HTML certificate uses (Cinzel +
# Cormorant Garamond). Falls back to the built-in serif fonts if the bundled
# TTFs are ever missing, so PDF generation can never hard-fail.
# ---------------------------------------------------------------------------

_FONT_DIR = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "fonts"
)

# Resolved font names (populated by _register_fonts). These mirror the exact
# four-family hierarchy used by the HTML certificate:
#   Cinzel            -> headings / titles / caps
#   Cormorant Garamond-> recipient name + decorative lead-ins
#   Inter             -> body copy / labels / meta
#   Libre Baskerville -> footer values / founder block / security note
F_HEADING = "Times-Bold"          # Cinzel-Bold  -> titles / caps
F_HEADING_MED = "Times-Bold"      # Cinzel-SemiBold -> org name / ribbon / seal
F_BODY = "Times-Roman"            # Cormorant SemiBold
F_BODY_BOLD = "Times-Bold"        # Cormorant Bold -> recipient name
F_BODY_ITALIC = "Times-Italic"    # Cormorant SemiBold Italic -> lead-in
F_BODY_BOLD_ITALIC = "Times-BoldItalic"
F_SANS = "Helvetica"              # Inter Regular -> body copy
F_SANS_MED = "Helvetica-Bold"     # Inter SemiBold -> labels / meta
F_SANS_BOLD = "Helvetica-Bold"    # Inter Bold
F_FOOTER = "Times-Roman"          # Libre Baskerville Regular
F_FOOTER_BOLD = "Times-Bold"      # Libre Baskerville Bold -> footer values / founder
F_FOOTER_ITALIC = "Times-Italic"  # Libre Baskerville Italic -> org / security note
_FONTS_READY = False


def _register_fonts():
    global F_HEADING, F_HEADING_MED, F_BODY, F_BODY_BOLD
    global F_BODY_ITALIC, F_BODY_BOLD_ITALIC
    global F_SANS, F_SANS_MED, F_SANS_BOLD
    global F_FOOTER, F_FOOTER_BOLD, F_FOOTER_ITALIC, _FONTS_READY

    if _FONTS_READY:
        return

    mapping = {
        "Cinzel-Bold": "Cinzel-Bold.ttf",
        "Cinzel-SemiBold": "Cinzel-SemiBold.ttf",
        "Cormorant-SemiBold": "CormorantGaramond-SemiBold.ttf",
        "Cormorant-Bold": "CormorantGaramond-Bold.ttf",
        "Cormorant-SemiBoldItalic": "CormorantGaramond-SemiBoldItalic.ttf",
        "Cormorant-BoldItalic": "CormorantGaramond-BoldItalic.ttf",
        "Inter-Regular": "Inter-Regular.ttf",
        "Inter-SemiBold": "Inter-SemiBold.ttf",
        "Inter-Bold": "Inter-Bold.ttf",
        "Libre-Regular": "LibreBaskerville-Regular.ttf",
        "Libre-Bold": "LibreBaskerville-Bold.ttf",
        "Libre-Italic": "LibreBaskerville-Italic.ttf",
    }

    registered = {}
    for name, filename in mapping.items():
        path = os.path.join(_FONT_DIR, filename)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = True
            except Exception:
                pass

    if "Cinzel-Bold" in registered:
        F_HEADING = "Cinzel-Bold"
        F_HEADING_MED = "Cinzel-SemiBold" if "Cinzel-SemiBold" in registered else "Cinzel-Bold"
    if "Cormorant-SemiBold" in registered:
        F_BODY = "Cormorant-SemiBold"
        F_BODY_BOLD = "Cormorant-Bold" if "Cormorant-Bold" in registered else "Cormorant-SemiBold"
        F_BODY_ITALIC = "Cormorant-SemiBoldItalic" if "Cormorant-SemiBoldItalic" in registered else "Cormorant-SemiBold"
        F_BODY_BOLD_ITALIC = "Cormorant-BoldItalic" if "Cormorant-BoldItalic" in registered else F_BODY_BOLD
    if "Inter-Regular" in registered:
        F_SANS = "Inter-Regular"
        F_SANS_MED = "Inter-SemiBold" if "Inter-SemiBold" in registered else "Inter-Regular"
        F_SANS_BOLD = "Inter-Bold" if "Inter-Bold" in registered else F_SANS_MED
    if "Libre-Regular" in registered:
        F_FOOTER = "Libre-Regular"
        F_FOOTER_BOLD = "Libre-Bold" if "Libre-Bold" in registered else "Libre-Regular"
        F_FOOTER_ITALIC = "Libre-Italic" if "Libre-Italic" in registered else "Libre-Regular"

    _FONTS_READY = True


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------

def _gradient_rect(c, x, y, w, h, colors, positions=None, horizontal=True):
    """Fill a rectangle with a linear gradient (clipped to the rect)."""
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    if horizontal:
        c.linearGradient(x, y, x + w, y, colors, positions, extend=True)
    else:
        c.linearGradient(x, y, x, y + h, colors, positions, extend=True)
    c.restoreState()


def _draw_top_strip(c, w, h):
    """Blue -> gold -> blue tricolour strip along the very top edge."""
    strip_h = 4 * mm
    _gradient_rect(
        c, 0, h - strip_h, w, strip_h,
        [PRIMARY, GOLD_MID, PRIMARY], [0.0, 0.5, 1.0], horizontal=True,
    )


def _draw_border(c, w, h, border_color=PRIMARY, gold_color=GOLD):
    # Thin outer blue frame so the gold border reads as the primary focus.
    c.setStrokeColor(border_color)
    c.setLineWidth(3.5)
    c.rect(10 * mm, 10 * mm, w - 20 * mm, h - 20 * mm)

    c.setStrokeColor(gold_color)
    c.setLineWidth(2.5)
    c.rect(15 * mm, 15 * mm, w - 30 * mm, h - 30 * mm)

    # Gold corner brackets (mirrors the .corner elements).
    L = 14 * mm
    c.setStrokeColor(gold_color)
    c.setLineWidth(3.5)
    for x, y, sx, sy in [
        (15 * mm, 15 * mm, 1, 1),
        (w - 15 * mm, 15 * mm, -1, 1),
        (15 * mm, h - 15 * mm, 1, -1),
        (w - 15 * mm, h - 15 * mm, -1, -1),
    ]:
        c.line(x, y, x + sx * L, y)
        c.line(x, y, x, y + sy * L)


def _draw_ribbon(c, w, h, text="CERTIFICATE OF EXCELLENCE"):
    """Slim gold gradient ribbon (pill) with small notched tails, centred at the
    very top — mirrors the compact HTML .gold-ribbon rather than a heavy banner."""
    label = (text or "")[:60]
    c.setFont(F_HEADING_MED, 8)
    text_w = c.stringWidth(label, F_HEADING_MED, 8)
    ribbon_w = text_w + 20 * mm
    ribbon_h = 6.4 * mm
    x = (w - ribbon_w) / 2
    y = h - 22 * mm

    _gradient_rect(
        c, x, y, ribbon_w, ribbon_h,
        [GOLD_DARK, GOLD_MID, GOLD_LIGHT, GOLD_MID, GOLD_DARK],
        [0.0, 0.25, 0.5, 0.75, 1.0], horizontal=True,
    )

    # Emboss: bright highlight line along the top edge, soft shadow at the base.
    c.setStrokeColor(HexColor("#fbedb4"))
    c.setLineWidth(0.8)
    c.line(x, y + ribbon_h - 0.4 * mm, x + ribbon_w, y + ribbon_h - 0.4 * mm)
    c.setStrokeColor(HexColor("#7a580e"))
    c.setLineWidth(0.8)
    c.line(x, y + 0.4 * mm, x + ribbon_w, y + 0.4 * mm)

    # Folded ribbon tails dipping below the banner, tucked inward.
    tail = 3.2 * mm
    c.setFillColor(HexColor("#7a580e"))
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x - tail, y - tail)
    p.lineTo(x, y - tail)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(x + ribbon_w, y)
    p.lineTo(x + ribbon_w + tail, y - tail)
    p.lineTo(x + ribbon_w, y - tail)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    c.setFillColor(INK)
    c.drawCentredString(w / 2, y + 2.1 * mm, label)


def _draw_crown(c, cx, cy, size, color):
    """A small three-point crown, drawn as a filled path (points up, valleys down)."""
    s = size
    c.saveState()
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx - s, cy - s * 0.55)                 # bottom-left
    p.lineTo(cx - s, cy + s * 0.45)                 # left point (tip)
    p.lineTo(cx - s * 0.42, cy - s * 0.15)          # left valley (down)
    p.lineTo(cx, cy + s * 0.75)                     # centre point (tallest)
    p.lineTo(cx + s * 0.42, cy - s * 0.15)          # right valley (down)
    p.lineTo(cx + s, cy + s * 0.45)                 # right point (tip)
    p.lineTo(cx + s, cy - s * 0.55)                 # bottom-right
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # Base bar beneath the points.
    c.rect(cx - s * 1.05, cy - s * 0.85, s * 2.1, s * 0.34, fill=1, stroke=0)
    c.restoreState()
    # Jewel tips.
    for tx, ty in [(cx - s, cy + s * 0.45), (cx, cy + s * 0.75), (cx + s, cy + s * 0.45)]:
        c.setFillColor(GOLD_LIGHT)
        c.circle(tx, ty, s * 0.14, fill=1, stroke=0)
    c.setFillColor(color)


def _draw_medallion(c, cx, cy, r=11 * mm):
    """Gold radial medallion with a blue crown (mirrors .logo-circle)."""
    c.saveState()
    p = c.beginPath()
    p.circle(cx, cy, r)
    c.clipPath(p, stroke=0, fill=0)
    c.radialGradient(cx + r * 0.25, cy + r * 0.35, r * 1.6,
                     [GOLD_LIGHT, GOLD_MID, GOLD_DARK], [0.0, 0.55, 1.0])
    c.restoreState()

    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(1)
    c.circle(cx, cy, r, fill=0, stroke=1)

    _draw_crown(c, cx, cy, r * 0.42, PRIMARY)


def _draw_watermark(c, w, h, text="TYPEMASTER INDIA"):
    # A whisper-faint diagonal watermark that sits behind all content, matching
    # the HTML's rgba(13,59,142,.045). Uses fill alpha for a true subtle blend.
    c.saveState()
    try:
        c.setFillColor(PRIMARY)
        c.setFillAlpha(0.035)
        c.setFont(F_HEADING, 52)
        c.translate(w / 2, h / 2)
        c.rotate(28)
        c.drawCentredString(0, 0, (text or "")[:40])
    finally:
        c.restoreState()


def _draw_seal(c, w, h, gold_color=GOLD):
    """Embossed gold seal, top-right, rotated like the HTML .gold-seal."""
    cx = w - 43 * mm
    cy = h - 43 * mm
    r = 14.9 * mm

    c.saveState()
    c.translate(cx, cy)
    c.rotate(-15)

    # Radial gold fill.
    c.saveState()
    p = c.beginPath()
    p.circle(0, 0, r)
    c.clipPath(p, stroke=0, fill=0)
    c.radialGradient(0, r * 0.3, r * 1.7,
                     [GOLD_LIGHT, GOLD_MID, GOLD_DARK], [0.0, 0.5, 1.0])
    c.restoreState()

    # Dashed inner ring.
    c.setStrokeColor(HexColor("#fff7db"))
    c.setLineWidth(1.2)
    c.setDash(3, 2)
    c.circle(0, 0, r * 0.78, fill=0, stroke=1)
    c.setDash()

    c.setFillColor(PRIMARY)
    c.setFont(F_HEADING_MED, 6)
    c.drawCentredString(0, r * 0.32, "EXCELLENCE")
    c.setFont(F_HEADING, 11)
    c.drawCentredString(0, -r * 0.08, "IN")
    c.setFont(F_HEADING_MED, 6)
    c.drawCentredString(0, -r * 0.44, "TYPING")

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

    box_h = 22 * mm
    for i, (label, value) in enumerate(items):
        x = start_x + i * (box_w + gap)
        # Warm paper fill + luxury gold border (mirrors the premium HTML card).
        c.setFillColor(HexColor("#fdf9ef"))
        c.setStrokeColor(HexColor("#d9bf6e"))
        c.setLineWidth(1.4)
        c.roundRect(x, y, box_w, box_h, 6, fill=1, stroke=1)
        # Label on top (Inter, tracked caps) · value below (Cormorant) — mirrors
        # the premium HTML stat card exactly.
        c.setFont(F_SANS_MED, 6.5)
        c.setFillColor(MUTED)
        c.drawCentredString(x + box_w / 2, y + 15 * mm, label.upper())
        c.setFont(F_BODY_BOLD, 24)
        c.setFillColor(PRIMARY)
        c.drawCentredString(x + box_w / 2, y + 5 * mm, str(value))


def _draw_qr(c, data, x, y, size):
    widget = QrCodeWidget(data)
    bounds = widget.getBounds()
    bw = bounds[2] - bounds[0]
    bh = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size / bw, 0, 0, size / bh, 0, 0])
    d.add(widget)
    renderPDF.draw(d, c, x, y)


def _hex_or(default, value):
    """Return a reportlab HexColor from a #rrggbb string, else the default."""
    try:
        if value and isinstance(value, str) and value.startswith("#") and len(value) in (4, 7):
            return HexColor(value)
    except Exception:
        pass
    return default


def create_certificate(path, result, certificate_id, user, verify_url=None):
    _register_fonts()

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
    show_logo = get_setting("cert_logo_enabled", True)
    watermark_text = get_setting("cert_watermark_text", "TYPEMASTER INDIA")
    title_text = get_setting("cert_title", "Certificate of Achievement")
    subtitle_text = get_setting("cert_subtitle", "Official Typing Performance Record")

    org = get_setting("org_name", "TypeMaster India")
    founder = get_setting("founder_name", "Sumit Goswami")
    founder_title = get_setting("founder_title", "Founder & CEO")
    footer_note = get_setting("certificate_footer", "Digitally generated and verifiable online.")

    # ---- Background (subtle warm paper split, like the CSS gradient) ----
    c.setFillColor(PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    _gradient_rect(c, 0, 0, w, h, [PAPER, PAPER_2], [0.0, 1.0], horizontal=False)

    if show_watermark:
        _draw_watermark(c, w, h, watermark_text)

    _draw_top_strip(c, w, h)
    _draw_border(c, w, h, border_color, gold_color)
    if show_ribbon:
        _draw_ribbon(c, w, h, ribbon_text)
    if show_seal:
        _draw_seal(c, w, h, gold_color)

    # ---- Header: medallion + org + title + subtitle ----
    # Keep clear separation between the medallion and the org name (no overlap),
    # mirroring the stacked HTML logo-area.
    if show_logo:
        # Larger medallion (premium focal point) with clear separation below.
        _draw_medallion(c, w / 2, h - 40 * mm, r=11.5 * mm)
        _centered(c, org.upper(), h - 56 * mm, F_HEADING_MED, 9.5, MUTED)
        title_y = h - 68 * mm
    else:
        _centered(c, org.upper(), h - 42 * mm, F_HEADING_MED, 9.5, MUTED)
        title_y = h - 54 * mm

    # Title — the visual hero.
    _centered(c, title_text.upper(), title_y, F_HEADING, 30, border_color)
    _centered(c, subtitle_text, title_y - 10 * mm, F_BODY_BOLD, 15, GOLD_DARK)

    # Gold divider, centred and aligned under the title stack.
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.5)
    c.line(w / 2 - 45 * mm, title_y - 15 * mm, w / 2 + 45 * mm, title_y - 15 * mm)

    _centered(c, "This is to certify that", title_y - 21 * mm, F_BODY_ITALIC, 13, MUTED)

    # Recipient name — Cormorant Garamond Bold, brand colour, title case
    # (mirrors .student-section h3), with generous white space around it.
    name_y = title_y - 34 * mm
    _centered(c, user.full_name, name_y, F_BODY_BOLD, 34, border_color)
    c.setStrokeColor(GOLD_LIGHT)
    c.setLineWidth(1.2)
    c.line(w / 2 - 58 * mm, name_y - 5 * mm, w / 2 + 58 * mm, name_y - 5 * mm)

    # Body copy — Inter (mirrors .student-section p).
    _centered(
        c,
        f"has successfully completed the {org} Typing Test with outstanding performance, accuracy and dedication.",
        name_y - 11 * mm,
        F_SANS,
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
    # Group the stats + meta directly beneath the body copy so the footer can
    # anchor the bottom edge — mirrors the HTML rhythm (no dead band mid-page).
    _stat_grid(c, w, 70 * mm, stats)

    meta = (
        f"Language: {result.language}      Difficulty: {result.difficulty}      "
        f"Duration: {result.duration}s      Layout: QWERTY"
    )
    _centered(c, meta, 63 * mm, F_SANS, 9, MUTED)

    # ---- Footer: cert no + date (left), QR (centre), signature (right) ----
    # The inner gold border sits at 15mm; keep EVERY footer element safely
    # above it so nothing ever touches or overlaps the border. The security
    # note is the single lowest line, still clear of the frame.
    right_x = w - 26 * mm
    left_x = 26 * mm

    # Left column: certificate number + issue date.
    # Micro-labels in Inter; values in Libre Baskerville Bold (footer family).
    c.setFont(F_SANS_MED, 6.5)
    c.setFillColor(MUTED)
    c.drawString(left_x, 44 * mm, "CERTIFICATE NO.")
    c.setFont(F_FOOTER_BOLD, 10)
    c.setFillColor(PRIMARY)
    c.drawString(left_x, 39 * mm, certificate_id)

    issue_date = result.created_at.strftime("%d %B %Y") if result.created_at else datetime.now().strftime("%d %B %Y")
    c.setFont(F_SANS_MED, 6.5)
    c.setFillColor(MUTED)
    c.drawString(left_x, 32 * mm, "DATE OF ISSUE")
    c.setFont(F_FOOTER_BOLD, 10)
    c.setFillColor(PRIMARY)
    c.drawString(left_x, 27 * mm, issue_date)

    # Centre column: QR + caption (Inter).
    if verify_url:
        qr_size = 24 * mm
        _draw_qr(c, verify_url, w / 2 - qr_size / 2, 28 * mm, qr_size)
        c.setFont(F_SANS_MED, 6.5)
        c.setFillColor(MUTED)
        c.drawCentredString(w / 2, 24 * mm, "SCAN TO VERIFY AUTHENTICITY")

    # Right column: signature image + line + founder details, nudged slightly
    # upward with generous spacing between each line (nothing cramped).
    sig_path = signature_abs_path()
    if sig_path and os.path.exists(sig_path):
        sig_w, sig_h = 45 * mm, 12 * mm
        c.drawImage(
            sig_path,
            right_x - sig_w,
            41 * mm,
            width=sig_w,
            height=sig_h,
            preserveAspectRatio=True,
            anchor="se",
            mask="auto",
        )
        c.setStrokeColor(HexColor("#444444"))
        c.setLineWidth(1)
        c.line(right_x - sig_w, 40 * mm, right_x, 40 * mm)
    else:
        c.setStrokeColor(HexColor("#444444"))
        c.setLineWidth(1)
        c.line(right_x - 45 * mm, 40 * mm, right_x, 40 * mm)

    # Founder block — name (Cinzel small-caps) · role (Inter tracked caps) ·
    # org (Libre Baskerville italic), mirroring the premium HTML footer family.
    name_y = 35 * mm
    c.setFont(F_HEADING, 12)
    c.setFillColor(PRIMARY)
    c.drawRightString(right_x, name_y, founder.upper())
    c.setFont(F_SANS_MED, 7)
    c.setFillColor(GOLD_DARK)
    c.drawRightString(right_x, name_y - 6 * mm, founder_title.upper())
    c.setFont(F_FOOTER_ITALIC, 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(right_x, name_y - 11.5 * mm, org)

    # Security note — single lowest line, still comfortably above the border.
    note = footer_note
    if verify_url and "Verify" not in note:
        note = f"{footer_note}  Verify at {verify_url}"
    c.setFont(F_FOOTER_ITALIC, 8)
    c.setFillColor(MUTED)
    c.drawCentredString(w / 2, 19.5 * mm, note)

    c.showPage()
    c.save()
