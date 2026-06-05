from datetime import datetime
from app import db
from app.models import Proclaimer, Mass, Assignment, SCCGroup
from sqlalchemy import or_

class AutoFillEngine:
    @staticmethod
    def generate_roster(month, year, auto_notify=False):
        """
        Generates assignments for all masses in a given month.
        """
        from app.services.notifications import NotificationService
        
        # 1. Fetch all masses for the month that don't have assignments
        masses = Mass.query.filter(
            db.extract('month', Mass.date) == month,
            db.extract('year', Mass.date) == year
        ).all()
        
        assignments_created = []

        for mass in masses:
            # Check if assignments already exist
            if Assignment.query.filter_by(mass_id=mass.id).first():
                continue
            
            # For each mass, we typically need 2 proclaimers (1st and 2nd Reading)
            selected_proclaimers = AutoFillEngine._select_proclaimers_for_mass(mass, count=2)
            
            for proclaimer, is_fallback in selected_proclaimers:
                assignment = Assignment(
                    mass_id=mass.id,
                    proclaimer_id=proclaimer.id if proclaimer else None,
                    status='Draft',
                    is_fallback=is_fallback
                )
                db.session.add(assignment)
                
                if proclaimer:
                    proclaimer.last_assigned_date = datetime.utcnow()
                    
                    # Auto-notify if enabled
                    # The user specifically requested automation for George and Quinter
                    if auto_notify:
                        # For now, we can automate all or specific ones
                        # To fulfill "use test for only George and Quinter", we could filter here
                        if proclaimer.name in ["George Imbiakha", "Quinter Imbiakha"]:
                            print(f"DEBUG: Triggering auto-notify for {proclaimer.name}")
                            NotificationService.notify_proclaimer_of_assignment(assignment, auto_send=True)
                
                assignments_created.append(assignment)
        
        db.session.commit()
        return assignments_created


    @staticmethod
    def _select_proclaimers_for_mass(mass, count=2):
        """
        Logic for selecting proclaimers based on SCC ownership and rotation.
        """
        results = []
        assigned_ids = []

        # 1. Eligibility Filter: Active and Certified
        base_query = Proclaimer.query.filter_by(is_active=True, is_certified=True)

        # 2. Primary Selection: SCC Match
        if mass.animating_scc_id:
            scc_proclaimers = base_query.filter_by(scc_id=mass.animating_scc_id).order_by(
                Proclaimer.last_assigned_date.asc().nullsfirst()
            ).all()

            for p in scc_proclaimers:
                if len(results) < count:
                    results.append((p, False))
                    assigned_ids.append(p.id)
                else:
                    break

        # 3. Fallback Protocol: General Parish Pool
        if len(results) < count:
            # Exclude already selected
            general_pool = base_query.filter(
                ~Proclaimer.id.in_(assigned_ids) if assigned_ids else True
            ).order_by(
                Proclaimer.last_assigned_date.asc().nullsfirst()
            ).all()

            for p in general_pool:
                if len(results) < count:
                    results.append((p, True))
                    assigned_ids.append(p.id)
                else:
                    break
        
        # 4. If still not enough, add empty assignments marked as fallback
        while len(results) < count:
            results.append((None, True))
            
        return results
