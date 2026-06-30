from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_certificate(path, result, certificate_id, user):

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate(path, pagesize=A4)

    story = []

    story.append(
        Paragraph("<b>TypeMaster India</b>", styles["Title"])
    )

    story.append(
        Paragraph(
            "Certificate of Achievement",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Name:</b> {user.full_name}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Net WPM:</b> {result.net_wpm}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Accuracy:</b> {result.accuracy}%",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Language:</b> {result.language}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Difficulty:</b> {result.difficulty}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Certificate ID:</b> {certificate_id}",
            styles["Normal"]
        )
    )

    pdf.build(story)