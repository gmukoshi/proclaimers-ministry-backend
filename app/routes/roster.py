from flask import Blueprint, jsonify, request
from app.services.scheduler import AutoFillEngine
from app.models import Assignment, Mass, Proclaimer
from app import db

roster_bp = Blueprint('roster', __name__, url_prefix='/api/roster')

@roster_bp.route('/generate', methods=['POST'])
def generate_roster():
    data = request.get_json()
    month = data.get('month')
    year = data.get('year')
    auto_notify = data.get('auto_notify', False)
    
    if not month or not year:
        return jsonify({"error": "Month and Year are required"}), 400
        
    assignments = AutoFillEngine.generate_roster(int(month), int(year), auto_notify=auto_notify)
    
    return jsonify({
        "message": f"Successfully generated roster for {month}/{year}",
        "assignments_count": len(assignments),
        "auto_notify_enabled": auto_notify
    }), 201


@roster_bp.route('/<int:year>/<int:month>', methods=['GET'])
def get_roster(year, month):
    assignments = Assignment.query.join(Mass).filter(
        db.extract('month', Mass.date) == month,
        db.extract('year', Mass.date) == year
    ).all()
    
    result = []
    for a in assignments:
        result.append({
            "id": a.id,
            "mass": {
                "id": a.mass.id,
                "date": a.mass.date.isoformat(),
                "time": a.mass.time.isoformat(),
                "language": a.mass.language
            },
            "proclaimer": {
                "id": a.proclaimer.id if a.proclaimer else None,
                "name": a.proclaimer.name if a.proclaimer else "Unassigned"
            } if a.proclaimer_id else None,
            "status": a.status,
            "is_fallback": a.is_fallback
        })
    
    return jsonify(result)
