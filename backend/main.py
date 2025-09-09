from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:111111@localhost/harms_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:3000'])

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum('patient', 'doctor', 'admin'), nullable=False, default='patient')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for doctors
    specialty = db.Column(db.String(100), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    
    # Additional fields for patients
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'specialty': self.specialty,
            'license_number': self.license_number,
            'experience_years': self.experience_years,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Routes
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'HARMS API is running'}

@app.route('/')
def root():
    return {
        'message': 'Healthcare Appointment & Resource Management System (HARMS) API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'appointments': '/api/appointments',
            'dashboard': '/api/dashboard',
            'resources': '/api/resources',
            'users': '/api/users'
        }
    }

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
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

@app.route('/api/auth/register', methods=['POST'])
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
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 8:
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
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            is_active=True
        )
        user.set_password(password)
        
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
        access_token = create_access_token(identity=str(user.id))
        
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

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        print(f"JWT Identity: {user_id}")  # Debug log
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")  # Debug log
        return jsonify({'error': 'An error occurred while fetching user data'}), 500

# Dashboard routes
@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic stats for now
        stats = {
            'appointments': {
                'total': 0,
                'scheduled': 0,
                'confirmed': 0,
                'completed': 0,
                'cancelled': 0
            },
            'upcoming_appointments': [],
            'resources': {
                'total_resources': 0,
                'total_beds': 0,
                'total_medicines': 0,
                'total_equipment': 0,
                'low_stock_count': 0,
                'expired_medicines': 0
            },
            'occupancy': {
                'total_beds': 0,
                'occupied_beds': 0,
                'available_beds': 0,
                'occupancy_rate': 0
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching dashboard stats'}), 500

@app.route('/api/dashboard/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic notifications for now
        notifications = []
        
        return jsonify({'notifications': notifications}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching notifications'}), 500

# Appointments routes
@app.route('/api/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic appointments for now
        appointments = []
        
        return jsonify({
            'appointments': appointments,
            'total': 0,
            'pages': 0,
            'current_page': 1,
            'per_page': 10
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching appointments'}), 500

@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        print(f"Received appointment data: {data}")  # Debug log
        
        # Validate required fields
        required_fields = ['doctor_id', 'appointment_date', 'appointment_time', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user is patient or admin
        if user.role not in ['patient', 'admin']:
            return jsonify({'error': 'Only patients can book appointments'}), 403
        
        # Validate doctor exists
        doctor = User.query.get(data['doctor_id'])
        if not doctor or doctor.role != 'doctor':
            return jsonify({'error': 'Invalid doctor'}), 400
        
        # For now, just return success without actually creating the appointment
        # In a real implementation, you would create an Appointment model and save it
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment_id': 1  # Mock ID
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while creating appointment'}), 500

@app.route('/api/appointments/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    try:
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'first_name': doctor.first_name,
                'last_name': doctor.last_name,
                'specialty': doctor.specialty,
                'experience_years': doctor.experience_years
            })
        
        return jsonify({'doctors': doctors_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching doctors'}), 500

@app.route('/api/appointments/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        date_str = request.args.get('date')
        
        print(f"Available slots request - doctor_id: {doctor_id}, date: {date_str}")  # Debug log
        
        if not doctor_id or not date_str:
            return jsonify({'error': 'doctor_id and date are required'}), 400
        
        # Validate date format (should be YYYY-MM-DD)
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            print(f"Parsed date: {parsed_date}")  # Debug log
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Generate available time slots (9 AM to 5 PM, 30-minute intervals)
        available_slots = []
        start_time = 9  # 9 AM
        end_time = 17   # 5 PM
        
        for hour in range(start_time, end_time):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                available_slots.append(time_str)
        
        print(f"Generated {len(available_slots)} available slots")  # Debug log
        return jsonify({'available_slots': available_slots}), 200
        
    except Exception as e:
        print(f"Error in get_available_slots: {str(e)}")  # Debug log
        return jsonify({'error': 'An error occurred while fetching available slots'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the app
    print("Starting HARMS API server...")
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True, host='0.0.0.0', port=5001)