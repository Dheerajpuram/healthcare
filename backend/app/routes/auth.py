from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app import db
from app.utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active
            },
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred during login'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role'].lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Validate role
        if role not in ['patient', 'doctor', 'admin']:
            return jsonify({'error': 'Invalid role. Must be patient, doctor, or admin'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User(
            email=email,
            password=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            is_active=True
        )
        
        # Add doctor-specific fields if role is doctor
        if role == 'doctor':
            user.specialty = data.get('specialty', '').strip() if data.get('specialty') else None
            user.license_number = data.get('license_number', '').strip() if data.get('license_number') else None
            user.experience_years = data.get('experience_years') if data.get('experience_years') else None
        
        # Add patient-specific fields if role is patient
        if role == 'patient':
            user.date_of_birth = data.get('date_of_birth') if data.get('date_of_birth') else None
            user.gender = data.get('gender') if data.get('gender') else None
            user.address = data.get('address', '').strip() if data.get('address') else None
            user.emergency_contact = data.get('emergency_contact', '').strip() if data.get('emergency_contact') else None
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active
            },
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'data': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'phone': user.phone,
                'specialty': user.specialty,
                'license_number': user.license_number,
                'experience_years': user.experience_years,
                'date_of_birth': user.date_of_birth,
                'gender': user.gender,
                'address': user.address,
                'emergency_contact': user.emergency_contact,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching user data'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real application, you would blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Successfully logged out'}), 200