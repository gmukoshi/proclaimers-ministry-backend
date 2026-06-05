from flask import Blueprint, jsonify, request
from app.models import Proclaimer, Assignment, Mass
from app.services.notifications import NotificationService
from app import db

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('/notify/<int:proclaimer_id>', methods=['POST'])
def notify_proclaimer(proclaimer_id):
    proclaimer = Proclaimer.query.get_or_404(proclaimer_id)
    
    # Logic to find the next assignment for this proclaimer
    assignment = Assignment.query.filter_by(proclaimer_id=proclaimer.id).join(Mass).order_by(Mass.date.asc()).first()
    
    if not assignment:
        return jsonify({"error": "No upcoming assignment found for this proclaimer"}), 404
        
    success, link = NotificationService.notify_proclaimer_of_assignment(assignment)
    
    if success:
        return jsonify({
            "message": f"Successfully prepared WhatsApp notification for {proclaimer.name}",
            "whatsapp_link": link
        }), 200
    else:
        return jsonify({"error": "Failed to prepare notification"}), 500

@notifications_bp.route('/share-roster', methods=['POST'])
def share_roster():
    data = request.get_json()
    month = data.get('month')
    year = data.get('year')
    phone_number = data.get('phone_number') # Optional target
    
    if not month or not year:
        return jsonify({"error": "Month and Year are required"}), 400
        
    assignments = Assignment.query.join(Mass).filter(
        db.extract('month', Mass.date) == month,
        db.extract('year', Mass.date) == year
    ).order_by(Mass.date, Mass.time).all()
    
    if not assignments:
        return jsonify({"error": "No roster found for the given month/year"}), 404
        
    # Format a professional roster message
    roster_msg = f"📖 *Proclaimers Ministry Roster - {month}/{year}*\n\n"
    current_date = None
    for a in assignments:
        if a.mass.date != current_date:
            current_date = a.mass.date
            roster_msg += f"\n🗓 *{current_date.strftime('%d %b %Y')}*\n"
        
        p_name = a.proclaimer.name if a.proclaimer else "Unassigned"
        roster_msg += f"- {a.mass.time.strftime('%I:%M %p')}: {p_name}\n"
    
    roster_msg += "\nGod bless our ministry! 🙏"
    
    # If phone_number provided, return a wa.me link
    link = None
    if phone_number:
        _, link = NotificationService.send_whatsapp(phone_number, roster_msg)
        
    return jsonify({
        "message_text": roster_msg,
        "whatsapp_link": link
    }), 200
