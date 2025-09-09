from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.appointment import Appointment
from app.models.user import User
from app.models.resource import Resource
from app import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get appointment statistics
        appointment_query = Appointment.query
        
        if user.role == 'patient':
            appointment_query = appointment_query.filter_by(patient_id=user_id)
        elif user.role == 'doctor':
            appointment_query = appointment_query.filter_by(doctor_id=user_id)
        # Admin can see all appointments
        
        # Count appointments by status
        appointments = appointment_query.all()
        
        stats = {
            'appointments': {
                'total': len(appointments),
                'scheduled': len([a for a in appointments if a.status == 'scheduled']),
                'confirmed': len([a for a in appointments if a.status == 'confirmed']),
                'completed': len([a for a in appointments if a.status == 'completed']),
                'cancelled': len([a for a in appointments if a.status == 'cancelled'])
            }
        }
        
        # Get upcoming appointments (next 7 days)
        upcoming_date = date.today() + timedelta(days=7)
        upcoming_appointments = appointment_query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.appointment_date <= upcoming_date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).limit(5).all()
        
        upcoming_data = []
        for appointment in upcoming_appointments:
            patient = User.query.get(appointment.patient_id)
            doctor = User.query.get(appointment.doctor_id)
            
            upcoming_data.append({
                'id': appointment.id,
                'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                'doctor_name': f"{doctor.first_name} {doctor.last_name}" if doctor else "Unknown",
                'appointment_date': appointment.appointment_date.isoformat(),
                'appointment_time': appointment.appointment_time,
                'status': appointment.status
            })
        
        stats['upcoming_appointments'] = upcoming_data
        
        # Get resource statistics (for admin only)
        if user.role == 'admin':
            resources = Resource.query.all()
            stats['resources'] = {
                'total_resources': len(resources),
                'total_beds': len([r for r in resources if r.resource_type == 'bed']),
                'total_medicines': len([r for r in resources if r.resource_type == 'medicine']),
                'total_equipment': len([r for r in resources if r.resource_type == 'equipment']),
                'low_stock_count': len([r for r in resources if r.available_quantity <= r.min_threshold]),
                'expired_medicines': len([r for r in resources if r.resource_type == 'medicine' and r.expiry_date and r.expiry_date < date.today()])
            }
            
            # Bed occupancy
            bed_resources = Resource.query.filter_by(resource_type='bed').all()
            total_beds = sum(r.total_quantity for r in bed_resources)
            occupied_beds = sum(r.total_quantity - r.available_quantity for r in bed_resources)
            
            stats['occupancy'] = {
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'available_beds': total_beds - occupied_beds,
                'occupancy_rate': round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 2)
            }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching dashboard stats'}), 500

@dashboard_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        notifications = []
        
        # Get upcoming appointments (next 24 hours)
        tomorrow = date.today() + timedelta(days=1)
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_date == tomorrow,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
        
        if user.role == 'patient':
            upcoming_appointments = upcoming_appointments.filter_by(patient_id=user_id)
        elif user.role == 'doctor':
            upcoming_appointments = upcoming_appointments.filter_by(doctor_id=user_id)
        
        for appointment in upcoming_appointments:
            patient = User.query.get(appointment.patient_id)
            doctor = User.query.get(appointment.doctor_id)
            
            if user.role == 'patient':
                notifications.append({
                    'type': 'appointment_reminder',
                    'title': 'Upcoming Appointment',
                    'message': f'You have an appointment with Dr. {doctor.last_name} tomorrow at {appointment.appointment_time}',
                    'date': appointment.appointment_date.isoformat(),
                    'priority': 'medium'
                })
            elif user.role == 'doctor':
                notifications.append({
                    'type': 'appointment_reminder',
                    'title': 'Upcoming Appointment',
                    'message': f'You have an appointment with {patient.first_name} {patient.last_name} tomorrow at {appointment.appointment_time}',
                    'date': appointment.appointment_date.isoformat(),
                    'priority': 'medium'
                })
        
        # Get low stock notifications (for admin only)
        if user.role == 'admin':
            low_stock_resources = Resource.query.filter(
                Resource.available_quantity <= Resource.min_threshold
            ).all()
            
            for resource in low_stock_resources:
                notifications.append({
                    'type': 'low_stock',
                    'title': 'Low Stock Alert',
                    'message': f'{resource.name} is running low. Available: {resource.available_quantity}',
                    'date': datetime.now().isoformat(),
                    'priority': 'high'
                })
            
            # Get expired medicines
            expired_medicines = Resource.query.filter(
                Resource.resource_type == 'medicine',
                Resource.expiry_date < date.today()
            ).all()
            
            for medicine in expired_medicines:
                notifications.append({
                    'type': 'expired',
                    'title': 'Expired Medicine',
                    'message': f'{medicine.name} has expired on {medicine.expiry_date}',
                    'date': datetime.now().isoformat(),
                    'priority': 'high'
                })
        
        return jsonify({'notifications': notifications}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching notifications'}), 500
