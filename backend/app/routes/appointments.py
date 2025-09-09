from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.appointment import Appointment
from app.models.user import User
from app import db
from datetime import datetime, date
from sqlalchemy import and_, or_

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        date_filter = request.args.get('date')
        
        # Build query based on user role
        query = Appointment.query
        
        if user.role == 'patient':
            query = query.filter_by(patient_id=user_id)
        elif user.role == 'doctor':
            query = query.filter_by(doctor_id=user_id)
        # Admin can see all appointments
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date == filter_date)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get appointments with pagination
        appointments = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format response
        appointments_data = []
        for appointment in appointments.items:
            # Get patient and doctor names
            patient = User.query.get(appointment.patient_id)
            doctor = User.query.get(appointment.doctor_id)
            
            appointments_data.append({
                'id': appointment.id,
                'patient_id': appointment.patient_id,
                'doctor_id': appointment.doctor_id,
                'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                'doctor_name': f"{doctor.first_name} {doctor.last_name}" if doctor else "Unknown",
                'appointment_date': appointment.appointment_date.isoformat(),
                'appointment_time': appointment.appointment_time,
                'duration_minutes': appointment.duration_minutes,
                'status': appointment.status,
                'reason': appointment.reason,
                'notes': appointment.notes,
                'created_at': appointment.created_at.isoformat() if appointment.created_at else None,
                'updated_at': appointment.updated_at.isoformat() if appointment.updated_at else None
            })
        
        return jsonify({
            'appointments': appointments_data,
            'total': appointments.total,
            'pages': appointments.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching appointments'}), 500

@appointments_bp.route('/', methods=['POST'])
@jwt_required()
def create_appointment():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['doctor_id', 'appointment_date', 'appointment_time', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user is patient or admin
        user = User.query.get(user_id)
        if user.role not in ['patient', 'admin']:
            return jsonify({'error': 'Only patients can book appointments'}), 403
        
        # Validate doctor exists
        doctor = User.query.get(data['doctor_id'])
        if not doctor or doctor.role != 'doctor':
            return jsonify({'error': 'Invalid doctor'}), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=user_id if user.role == 'patient' else data.get('patient_id', user_id),
            doctor_id=data['doctor_id'],
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=data['appointment_time'],
            duration_minutes=data.get('duration_minutes', 30),
            status='scheduled',
            reason=data['reason'],
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment_id': appointment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating appointment'}), 500

@appointments_bp.route('/doctors', methods=['GET'])
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

@appointments_bp.route('/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        date_str = request.args.get('date')
        
        if not doctor_id or not date_str:
            return jsonify({'error': 'doctor_id and date are required'}), 400
        
        # Parse date
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get existing appointments for the doctor on that date
        existing_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        ).all()
        
        # Generate available time slots (9 AM to 5 PM, 30-minute intervals)
        available_slots = []
        start_time = 9  # 9 AM
        end_time = 17   # 5 PM
        
        for hour in range(start_time, end_time):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                
                # Check if this slot is available
                is_available = True
                for appointment in existing_appointments:
                    if appointment.appointment_time == time_str:
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(time_str)
        
        return jsonify({'available_slots': available_slots}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching available slots'}), 500
