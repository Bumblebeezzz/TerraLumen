"""
PDF Membership Card Generation
"""

from flask import make_response
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_membership_card(user):
    """Generate a PDF membership card for the user"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Colors matching TerraLumen brand
    forest_green = colors.HexColor('#1A3C34')
    soft_gold = colors.HexColor('#D4AF37')
    plasma_aqua = colors.HexColor('#7CC2B7')
    charcoal = colors.HexColor('#353535')
    
    # Background
    c.setFillColor(colors.HexColor('#F2F1E8'))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Card dimensions (business card size: 3.5" x 2")
    card_width = 3.5 * inch
    card_height = 2 * inch
    card_x = (width - card_width) / 2
    card_y = (height - card_height) / 2
    
    # Card background (white)
    c.setFillColor(colors.white)
    c.setStrokeColor(forest_green)
    c.setLineWidth(2)
    c.roundRect(card_x, card_y, card_width, card_height, 10, fill=1, stroke=1)
    
    # Header with gold accent
    c.setFillColor(soft_gold)
    c.rect(card_x, card_y + card_height - 0.5 * inch, card_width, 0.5 * inch, fill=1, stroke=0)
    
    # TerraLumen logo/text
    c.setFillColor(forest_green)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(card_x + 0.2 * inch, card_y + card_height - 0.35 * inch, "TerraLumen")
    
    # Member name
    c.setFillColor(charcoal)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(card_x + 0.2 * inch, card_y + card_height - 0.9 * inch, "Member:")
    c.setFont("Helvetica", 12)
    c.drawString(card_x + 0.2 * inch, card_y + card_height - 1.1 * inch, user.name)
    
    # Membership type
    if user.membership_type:
        c.setFillColor(plasma_aqua)
        c.setFont("Helvetica-Bold", 10)
        membership_text = user.membership_type.value.title() + " Member"
        c.drawString(card_x + 0.2 * inch, card_y + card_height - 1.3 * inch, membership_text)
    
    # Member ID
    c.setFillColor(charcoal)
    c.setFont("Helvetica", 8)
    member_id = f"ID: {str(user.id).zfill(6)}"
    c.drawString(card_x + 0.2 * inch, card_y + 0.2 * inch, member_id)
    
    # Valid date
    if user.created_at:
        valid_text = f"Member Since: {user.created_at.strftime('%Y')}"
        c.drawString(card_x + card_width - 1.5 * inch, card_y + 0.2 * inch, valid_text)
    
    # Status indicator
    if user.membership_status and user.membership_status.value == 'active':
        c.setFillColor(plasma_aqua)
        c.circle(card_x + card_width - 0.3 * inch, card_y + card_height - 0.3 * inch, 0.1 * inch, fill=1, stroke=0)
    
    c.save()
    buffer.seek(0)
    
    # Create response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=terralumen_membership_card_{user.id}.pdf'
    
    return response

