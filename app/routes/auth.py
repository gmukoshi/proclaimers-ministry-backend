from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app import db
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password, role=data.get('role', 'Proclaimer'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@auth_bp.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    user = User.query.filter_by(username=auth.get('username')).first()
    if not user:
        return jsonify({'message': 'User not found'}), 401
        
    if check_password_hash(user.password_hash, auth.get('password')):
        token = jwt.encode({
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
        
    return jsonify({'message': 'Invalid password'}), 401
