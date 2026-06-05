from flask import Blueprint, jsonify
from app.models import Assignment, Proclaimer, SCCGroup, Mass
from app import db
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/coverage', methods=['GET'])
def get_coverage():
    total_masses = Mass.query.count()
    if total_masses == 0:
        return jsonify({"coverage_rate": 0})
        
    confirmed_assignments = Assignment.query.filter_by(status='Confirmed').count()
    # Assuming 2 proclaimers per mass, so total roles = total_masses * 2
    total_roles = total_masses * 2
    
    coverage_rate = (confirmed_assignments / total_roles) * 100 if total_roles > 0 else 0
    
    return jsonify({
        "total_masses": total_masses,
        "total_roles": total_roles,
        "confirmed_roles": confirmed_assignments,
        "coverage_rate": round(coverage_rate, 2)
    })

@analytics_bp.route('/scc-participation', methods=['GET'])
def get_scc_participation():
    results = db.session.query(
        SCCGroup.name,
        func.count(Assignment.id).label('total_assignments')
    ).join(Proclaimer, Proclaimer.scc_id == SCCGroup.id)\
     .join(Assignment, Assignment.proclaimer_id == Proclaimer.id)\
     .group_by(SCCGroup.name).all()
     
    participation = {name: count for name, count in results}
    
    return jsonify(participation)

@analytics_bp.route('/reliability', methods=['GET'])
def get_average_reliability():
    avg_reliability = db.session.query(func.avg(Proclaimer.reliability_score)).scalar()
    
    return jsonify({
        "average_reliability_score": round(avg_reliability, 2) if avg_reliability else 0
    })
