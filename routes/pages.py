"""Simple static content pages (About / Privacy / Terms / Contact).

Kept content-driven so the professional footer never links to a dead page.
"""

from flask import Blueprint, render_template, abort

pages = Blueprint("pages", __name__)

_CONTACT = {
    "telegram": "https://t.me/+FfIHI4_s4aI0NWE1",
    "instagram": "https://www.instagram.com/cop_sumit_goswami/",
    "youtube": "https://youtube.com/sumitgoswamihacker",
    "x": "https://x.com/cop_sumit_",
}

_CONTENT = {
    "about": {
        "eyebrow": "Our Story",
        "title": "About TypeMaster India",
        "lead": "India's most advanced typing practice platform for English and Hindi Mangal, "
                "built to help aspirants crack SSC, Railway, UP Police, CPCT and more.",
        "sections": [
            ("Our Mission", "We make government-exam typing preparation accessible, accurate and "
                            "motivating. From real exam-style mock tests to detailed WPM and accuracy "
                            "analytics, every feature is designed to get you exam-ready faster."),
            ("What We Offer", "English and Hindi (Mangal) practice, adaptive mock tests, custom "
                              "practice with OCR import, downloadable fonts and software, verifiable "
                              "certificates, leaderboards and progress tracking."),
            ("Built in India", "TypeMaster India is proudly built and maintained by Sumit Goswami for "
                               "Indian typists preparing for competitive examinations."),
        ],
    },
    "privacy": {
        "eyebrow": "Legal",
        "title": "Privacy Policy",
        "lead": "Your privacy matters. This policy explains what we collect and how we use it.",
        "sections": [
            ("Information We Collect", "We store the account details you provide (name, username, email, "
                                       "mobile) and your typing results to power analytics, leaderboards "
                                       "and certificates."),
            ("How We Use It", "Your data is used only to operate the platform — tracking progress, "
                              "issuing certificates and improving your experience. We never sell your data."),
            ("Data Security", "Passwords are stored using industry-standard hashing. Certificate "
                              "verification uses unguessable tokens unique to each certificate."),
            ("Contact", "For any privacy question, reach us on Telegram."),
        ],
    },
    "terms": {
        "eyebrow": "Legal",
        "title": "Terms of Use",
        "lead": "By using TypeMaster India you agree to the following terms.",
        "sections": [
            ("Acceptable Use", "Use the platform for personal typing practice and exam preparation. "
                               "Do not attempt to disrupt, reverse-engineer or abuse the service."),
            ("Accounts", "You are responsible for keeping your account credentials secure and for all "
                         "activity under your account."),
            ("Certificates", "Certificates reflect performance on a specific test and are verifiable "
                             "online. Tampering with or misrepresenting a certificate is prohibited."),
            ("Changes", "We may update these terms as the platform evolves. Continued use means you "
                        "accept the latest version."),
        ],
    },
    "contact": {
        "eyebrow": "Get in Touch",
        "title": "Contact Us",
        "lead": "Questions, feedback or partnership ideas? We'd love to hear from you.",
        "sections": [
            ("Telegram", "The fastest way to reach us — join our community channel."),
            ("Social", "Follow along on Instagram, YouTube and X for tips and updates."),
        ],
    },
}


@pages.route("/about")
def about():
    return _render("about")


@pages.route("/privacy")
def privacy():
    return _render("privacy")


@pages.route("/terms")
def terms():
    return _render("terms")


@pages.route("/contact")
def contact():
    return _render("contact")


def _render(slug):
    data = _CONTENT.get(slug)
    if not data:
        abort(404)
    return render_template("pages/static_page.html", page=data, contact=_CONTACT, slug=slug)
