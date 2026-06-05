from datetime import datetime
from app import db

class SCCGroup(db.Model):
    __tablename__ = 'scc_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    parish_rank = db.Column(db.Integer, default=1)
    representative_contact = db.Column(db.String(100))
    
    proclaimers = db.relationship('Proclaimer', backref='scc', lazy='dynamic')
    masses = db.relationship('Mass', backref='animating_scc', lazy='dynamic')

class Proclaimer(db.Model):
    __tablename__ = 'proclaimers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scc_id = db.Column(db.Integer, db.ForeignKey('scc_groups.id'))
    is_certified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20))
    reliability_score = db.Column(db.Float, default=100.0)
    last_assigned_date = db.Column(db.DateTime, index=True)
    
    assignments = db.relationship('Assignment', backref='proclaimer', lazy='dynamic')

class Mass(db.Model):
    __tablename__ = 'masses'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    language = db.Column(db.String(20), nullable=False) # English, Swahili, Latin
    animating_scc_id = db.Column(db.Integer, db.ForeignKey('scc_groups.id'))
    feast_day_details = db.Column(db.String(200))
    
    assignments = db.relationship('Assignment', backref='mass', lazy='dynamic')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    mass_id = db.Column(db.Integer, db.ForeignKey('masses.id'), nullable=False)
    proclaimer_id = db.Column(db.Integer, db.ForeignKey('proclaimers.id'))
    status = db.Column(db.String(20), default='Draft') # Draft, Pending, Confirmed, Declined, Fallback
    is_fallback = db.Column(db.Boolean, default=False)
    notification_sent = db.Column(db.Boolean, default=False)
    notification_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='Proclaimer') # Admin, Proclaimer
    
    def __repr__(self):
        return f'<User {self.username}>'
