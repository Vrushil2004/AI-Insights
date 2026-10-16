from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def render_pdf_report(report, filename="report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = [Paragraph("AI Insights Report", styles["Title"])]
    
    for key,value in report.items():
        content += [
        Paragraph(key.replace("_","").title(),styles["Heading2"]),
        Paragraph(str(value), styles["BodyText"])]
        
    
    doc.build(content)
    return filename