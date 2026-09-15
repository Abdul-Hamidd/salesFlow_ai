from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, date
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.supabase_tool import supabase


def get_report_data(report_date: date = None) -> dict:
    """Get all data needed for daily report"""
    
    if not report_date:
        report_date = date.today()
    
    date_str = report_date.isoformat()
    next_date_str = date(report_date.year, report_date.month, report_date.day + 1).isoformat() if report_date.day < 28 else date_str
    
    try:
        # Total contacts
        total_contacts = supabase.table("contacts").select("*", count="exact").execute().count
        
        # New contacts today
        new_contacts = supabase.table("contacts").select("*", count="exact").gte(
            "created_at", f"{date_str}T00:00:00"
        ).execute().count
        
        # Total messages today
        total_messages = supabase.table("conversations").select("*", count="exact").gte(
            "created_at", f"{date_str}T00:00:00"
        ).execute().count
        
        # Inbound messages today
        inbound_messages = supabase.table("conversations").select("*", count="exact").eq(
            "direction", "inbound"
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        # Outbound messages today
        outbound_messages = supabase.table("conversations").select("*", count="exact").eq(
            "direction", "outbound"
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        # Leads by status
        hot_leads = supabase.table("leads").select("*", count="exact").eq("status", "hot").execute().count
        warm_leads = supabase.table("leads").select("*", count="exact").eq("status", "warm").execute().count
        cold_leads = supabase.table("leads").select("*", count="exact").eq("status", "cold").execute().count
        
        # New leads today
        new_leads_today = supabase.table("leads").select("*", count="exact").gte(
            "created_at", f"{date_str}T00:00:00"
        ).execute().count
        
        # Total orders
        total_orders = supabase.table("orders").select("*", count="exact").execute().count
        
        # Revenue
        revenue_data = supabase.table("orders").select("total_price").eq("status", "delivered").execute()
        total_revenue = sum([r["total_price"] or 0 for r in revenue_data.data])
        
        # Follow ups sent today
        followups_sent = supabase.table("follow_ups").select("*", count="exact").eq(
            "is_sent", True
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        # Sentiment analysis
        positive = supabase.table("conversations").select("*", count="exact").eq(
            "sentiment", "positive"
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        negative = supabase.table("conversations").select("*", count="exact").eq(
            "sentiment", "negative"
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        neutral = supabase.table("conversations").select("*", count="exact").eq(
            "sentiment", "neutral"
        ).gte("created_at", f"{date_str}T00:00:00").execute().count
        
        # Recent contacts
        recent_contacts = supabase.table("contacts").select(
            "name, phone_number, created_at"
        ).order("created_at", desc=True).limit(5).execute().data
        
        # Top leads
        top_leads = supabase.table("leads").select(
            "score, status, contacts(name, phone_number)"
        ).order("score", desc=True).limit(5).execute().data
        
        return {
            "report_date": report_date,
            "total_contacts": total_contacts or 0,
            "new_contacts": new_contacts or 0,
            "total_messages": total_messages or 0,
            "inbound_messages": inbound_messages or 0,
            "outbound_messages": outbound_messages or 0,
            "hot_leads": hot_leads or 0,
            "warm_leads": warm_leads or 0,
            "cold_leads": cold_leads or 0,
            "new_leads_today": new_leads_today or 0,
            "total_orders": total_orders or 0,
            "total_revenue": total_revenue or 0,
            "followups_sent": followups_sent or 0,
            "positive_sentiment": positive or 0,
            "negative_sentiment": negative or 0,
            "neutral_sentiment": neutral or 0,
            "recent_contacts": recent_contacts or [],
            "top_leads": top_leads or []
        }
        
    except Exception as e:
        print(f"[Report] Error getting data: {e}")
        return {}


def generate_pdf_report(report_date: date = None) -> str:
    """Generate PDF report and return file path"""
    
    if not report_date:
        report_date = date.today()
    
    # Get data
    data = get_report_data(report_date)
    
    if not data:
        print("[Report] No data available")
        return None
    
    # File path
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    file_path = os.path.join(reports_dir, f"report_{report_date.isoformat()}.pdf")
    
    # Create PDF
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#075e54'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#888888'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#075e54'),
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Build content
    content = []
    
    # Header
    content.append(Paragraph("WhatsApp AI CRM", title_style))
    content.append(Paragraph(f"Daily Business Report — {report_date.strftime('%B %d, %Y')}", subtitle_style))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#25D366')))
    content.append(Spacer(1, 15))
    
    # Generated time
    content.append(Paragraph(
        f"Generated at: {datetime.now().strftime('%I:%M %p')}",
        ParagraphStyle('small', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_RIGHT)
    ))
    content.append(Spacer(1, 10))
    
    # Summary Stats
    content.append(Paragraph("📊 Summary Overview", heading_style))
    
    summary_data = [
        ['Metric', 'Today', 'Total'],
        ['New Contacts', str(data['new_contacts']), str(data['total_contacts'])],
        ['Messages', str(data['total_messages']), '—'],
        ['Inbound', str(data['inbound_messages']), '—'],
        ['Outbound', str(data['outbound_messages']), '—'],
        ['New Leads', str(data['new_leads_today']), '—'],
        ['Follow Ups Sent', str(data['followups_sent']), '—'],
        ['Total Orders', '—', str(data['total_orders'])],
        ['Total Revenue', '—', f"Rs. {data['total_revenue']:,.0f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 100, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#075e54')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 15))
    
    # Leads Overview
    content.append(Paragraph("🔥 Leads Overview", heading_style))
    
    leads_data = [
        ['Lead Type', 'Count', 'Status'],
        ['Hot Leads 🔥', str(data['hot_leads']), 'Ready to Buy'],
        ['Warm Leads ⚡', str(data['warm_leads']), 'Interested'],
        ['Cold Leads ❄️', str(data['cold_leads']), 'Needs Nurturing'],
        ['TOTAL', str(data['hot_leads'] + data['warm_leads'] + data['cold_leads']), '—'],
    ]
    
    leads_table = Table(leads_data, colWidths=[150, 100, 150])
    leads_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#075e54')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff0f0')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fff8f0')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f0f8ff')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    content.append(leads_table)
    content.append(Spacer(1, 15))
    
    # Sentiment Analysis
    content.append(Paragraph("😊 Customer Sentiment Analysis", heading_style))
    
    sentiment_data = [
        ['Sentiment', 'Count', 'Indicator'],
        ['😊 Positive', str(data['positive_sentiment']), 'Happy Customers'],
        ['😐 Neutral', str(data['neutral_sentiment']), 'Normal Interaction'],
        ['😠 Negative', str(data['negative_sentiment']), 'Needs Attention!'],
    ]
    
    sentiment_table = Table(sentiment_data, colWidths=[150, 100, 150])
    sentiment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#075e54')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    content.append(sentiment_table)
    content.append(Spacer(1, 15))
    
    # Top Leads
    if data['top_leads']:
        content.append(Paragraph("🏆 Top Leads", heading_style))
        
        top_leads_data = [['Customer', 'Phone', 'Score', 'Status']]
        for lead in data['top_leads']:
            contact = lead.get('contacts', {}) or {}
            top_leads_data.append([
                contact.get('name', 'Unknown'),
                contact.get('phone_number', '—'),
                f"{lead['score']}/100",
                lead['status'].upper()
            ])
        
        top_leads_table = Table(top_leads_data, colWidths=[120, 120, 80, 80])
        top_leads_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#075e54')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(top_leads_table)
        content.append(Spacer(1, 15))
    
    # Footer
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#25D366')))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "Generated by WhatsApp AI CRM System | Powered by Ollama AI",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=9,
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(content)
    print(f"[Report] ✅ PDF generated: {file_path}")
    
    return file_path


if __name__ == "__main__":
    # Test report generation
    path = generate_pdf_report()
    print(f"Report saved at: {path}")