import os
import io
import csv
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(analysis: dict) -> bytes:
    """
    Generates a professional PDF Analysis Report from stored analysis data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#059669') # Emerald-600
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563')
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151')
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#9CA3AF')
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("PlantIntel AI — Plant Disease Intelligence Report", title_style))
    story.append(Paragraph(f"Analysis ID: <b>{analysis.get('analysis_id')}</b> | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 10))

    # Summary Card Table
    pred_class = analysis.get("predicted_class", "N/A").replace("ImageNet class: ", "").replace("___", " - ").replace("_", " ")
    conf_pct = f"{(float(analysis.get('confidence', 0)) * 100):.2f}%"
    severity_pct = f"{float(analysis.get('severity_percentage', 0)):.2f}%"
    severity_level = analysis.get("severity_level", "N/A")

    summary_data = [
        [Paragraph("<b>Predicted Disease:</b>", body_style), Paragraph(f"<b>{pred_class}</b>", body_style)],
        [Paragraph("<b>Model Confidence:</b>", body_style), Paragraph(conf_pct, body_style)],
        [Paragraph("<b>Severity Category:</b>", body_style), Paragraph(f"{severity_level} ({severity_pct} affected leaf area)", body_style)],
        [Paragraph("<b>Model Backbone:</b>", body_style), Paragraph(f"{analysis.get('model_name', 'EfficientNetV2-S')} ({analysis.get('model_mode', 'attention')})", body_style)],
        [Paragraph("<b>Explainable AI Method:</b>", body_style), Paragraph("Grad-CAM++ & Adaptive Attention", body_style)]
    ]

    summary_table = Table(summary_data, colWidths=[150, 375])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Top Predictions Breakdown
    top_preds = analysis.get("top_predictions", [])
    if top_preds:
        story.append(Paragraph("Top Classification Candidates", section_style))
        pred_table_data = [["Rank", "Disease Candidate", "Model Confidence"]]
        for idx, item in enumerate(top_preds[:5]):
            name = item.get("class_name", "").replace("ImageNet class: ", "").replace("___", " - ").replace("_", " ")
            conf = f"{(float(item.get('confidence', 0)) * 100):.2f}%"
            pred_table_data.append([f"#{idx+1}", name, conf])

        pred_table = Table(pred_table_data, colWidths=[50, 340, 135])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(pred_table)
        story.append(Spacer(1, 12))

    # Severity Analysis Detail
    story.append(Paragraph("Disease Severity & Area Estimation", section_style))
    area_data = [
        ["Total Leaf Boundary Pixels", f"{analysis.get('leaf_area_pixels', 0):,} px"],
        ["Isolated Affected Pixels", f"{analysis.get('affected_area_pixels', 0):,} px"],
        ["Estimated Affected Percentage", severity_pct],
        ["Severity Classification Level", severity_level]
    ]
    area_table = Table(area_data, colWidths=[260, 265])
    area_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(area_table)
    story.append(Spacer(1, 15))

    # Mandatory Legal & Scientific Limitation Disclaimer
    story.append(Paragraph("<b>Scientific & Legal Disclaimer Notice:</b>", section_style))
    disclaimer_text = (
        "AI-assisted analysis only. Results depend on image quality, training data, model performance, and the severity-estimation method. "
        "The explanation visualizations indicate model-associated image regions and should not be interpreted as ground-truth disease segmentation."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_history_csv_string(items: list) -> str:
    """
    Generates a CSV string from a list of Analysis records.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "analysis_id",
        "created_at",
        "predicted_class",
        "confidence",
        "severity_percentage",
        "severity_level",
        "leaf_area_pixels",
        "affected_area_pixels",
        "model_name",
        "model_version"
    ])

    for item in items:
        writer.writerow([
            item.id,
            item.created_at.isoformat() if item.created_at else "",
            item.predicted_class,
            round(float(item.confidence), 4),
            round(float(item.severity_percentage), 2),
            item.severity_level,
            item.leaf_area_pixels,
            item.affected_area_pixels,
            item.model_name,
            item.model_version or ""
        ])

    return output.getvalue()
