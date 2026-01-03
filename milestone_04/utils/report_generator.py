# utils/report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import os

def generate_pdf(history_data, filename="dashboard/exports/report.pdf"):
    os.makedirs("dashboard/exports", exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Crowd Count System Report", styles['Title']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table header
    data = [["Time", "Total People"]]
    zone_ids = sorted(set(zid for entry in history_data for zid in entry['zones'].keys()))
    for zid in zone_ids:
        data[0].append(f"Zone {zid}")

    # Table rows
    for entry in history_data:
        row = [entry['time'], entry['total']]
        for zid in zone_ids:
            row.append(entry['zones'].get(zid, 0))
        data.append(row)

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige)
    ]))
    elements.append(table)
    doc.build(elements)
    return filename