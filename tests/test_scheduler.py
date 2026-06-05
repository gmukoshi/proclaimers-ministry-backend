import unittest
from datetime import date, time, datetime
from app import create_app, db
from app.models import Proclaimer, SCCGroup, Mass, Assignment
from app.services.scheduler import AutoFillEngine
from config import Config

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

class SchedulerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed data
        scc1 = SCCGroup(name="SCC 1")
        scc2 = SCCGroup(name="SCC 2")
        db.session.add_all([scc1, scc2])
        db.session.commit()

        p1 = Proclaimer(name="Proclaimer 1", scc_id=scc1.id, is_certified=True, is_active=True)
        p2 = Proclaimer(name="Proclaimer 2", scc_id=scc1.id, is_certified=True, is_active=True)
        p3 = Proclaimer(name="Proclaimer 3", scc_id=scc2.id, is_certified=True, is_active=True)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        mass = Mass(date=date(2026, 6, 7), time=time(8, 0), language="English", animating_scc_id=scc1.id)
        db.session.add(mass)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_roster_generation(self):
        assignments = AutoFillEngine.generate_roster(6, 2026)
        self.assertEqual(len(assignments), 2)
        
        # Verify both are from SCC 1 (primary selection)
        p_ids = [a.proclaimer_id for a in assignments]
        p1 = Proclaimer.query.filter_by(name="Proclaimer 1").first()
        p2 = Proclaimer.query.filter_by(name="Proclaimer 2").first()
        self.assertIn(p1.id, p_ids)
        self.assertIn(p2.id, p_ids)
        
        # Verify fallback is False
        for a in assignments:
            self.assertFalse(a.is_fallback)

    def test_fallback_protocol(self):
        # Add a mass with an SCC that has no proclaimers
        scc3 = SCCGroup(name="SCC 3")
        db.session.add(scc3)
        db.session.commit()
        
        mass = Mass(date=date(2026, 6, 14), time=time(10, 0), language="Swahili", animating_scc_id=scc3.id)
        db.session.add(mass)
        db.session.commit()
        
        assignments = AutoFillEngine.generate_roster(6, 2026)
        # We expect 2 assignments for the first mass (already tested) and 2 for the second mass
        # The second mass should trigger fallback since SCC 3 has no proclaimers
        
        m2_assignments = Assignment.query.filter_by(mass_id=mass.id).all()
        self.assertEqual(len(m2_assignments), 2)
        for a in m2_assignments:
            self.assertTrue(a.is_fallback)

if __name__ == '__main__':
    unittest.main()
