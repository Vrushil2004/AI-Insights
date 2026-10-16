
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from xml.sax.saxutils import escape


def render_pdf_report(report, filename="report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#174A7E"),
        spaceBefore=12,
        spaceAfter=6,
    ))

    content = [
        Paragraph("AI Insights Report", styles["Title"]),
        Spacer(1, 8),
        HRFlowable(width="100%", color=colors.HexColor("#174A7E")),
        Spacer(1, 12),
    ]

    for key, value in report.items():
        content.append(
            Paragraph(escape(key.replace("_", " ").title()), styles["Section"])
        )

        if isinstance(value, list):
            items = value or ["No information available."]
            for item in items:
                content.append(
                    Paragraph("• " + escape(str(item)), styles["BodyText"])
                )
                content.append(Spacer(1, 4))
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                content.append(Paragraph(
                    f"<b>{escape(str(subkey).replace('_', ' ').title())}:</b> "
                    f"{escape(str(subvalue))}",
                    styles["BodyText"],
                ))
        else:
            content.append(
                Paragraph(escape(str(value)), styles["BodyText"])
            )

        content.append(Spacer(1, 8))

    doc.build(content)
    return filename
