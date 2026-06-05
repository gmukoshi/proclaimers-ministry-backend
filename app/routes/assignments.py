from flask import Blueprint, jsonify, request
from app.models import Assignment, Proclaimer
from app import db
from datetime import datetime

assignment_bp = Blueprint('assignment', __name__, url_prefix='/api/assignments')

@assignment_bp.route('/<int:id>/status', methods=['PATCH'])
def update_status(id):
    assignment = Assignment.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    
    valid_statuses = ['Draft', 'Pending', 'Confirmed', 'Declined', 'No-show']
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400
        
    assignment.status = new_status
    
    # Logic for reliability score calculation
    if new_status == 'No-show' and assignment.proclaimer:
        # Deduct reliability score
        assignment.proclaimer.reliability_score = max(0, assignment.proclaimer.reliability_score - 10)
    elif new_status == 'Confirmed' and assignment.proclaimer:
        # Slightly boost reliability score or keep at 100
        assignment.proclaimer.reliability_score = min(100, assignment.proclaimer.reliability_score + 1)

    db.session.commit()
    
    return jsonify({"message": "Status updated successfully", "status": assignment.status})

@assignment_bp.route('/<int:id>/override', methods=['PATCH'])
def manual_override(id):
    assignment = Assignment.query.get_or_404(id)
    data = request.get_json()
    proclaimer_id = data.get('proclaimer_id')
    
    proclaimer = Proclaimer.query.get_or_404(proclaimer_id)
    assignment.proclaimer_id = proclaimer.id
    assignment.is_fallback = (proclaimer.scc_id != assignment.mass.animating_scc_id)
    
    db.session.commit()
    
    return jsonify({"message": "Assignment overridden successfully"})
