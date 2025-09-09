from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.resource import Resource
from app.models.user import User
from app import db
from datetime import datetime, date

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/', methods=['GET'])
@jwt_required()
def get_resources():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admin can access resources
        if user.role != 'admin':
            return jsonify({'error': 'Access denied. Admin role required'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        resource_type = request.args.get('type')
        
        # Build query
        query = Resource.query
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        # Get resources with pagination
        resources = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format response
        resources_data = []
        for resource in resources.items:
            resources_data.append({
                'id': resource.id,
                'name': resource.name,
                'resource_type': resource.resource_type,
                'category': resource.category,
                'total_quantity': resource.total_quantity,
                'available_quantity': resource.available_quantity,
                'unit': resource.unit,
                'description': resource.description,
                'location': resource.location,
                'expiry_date': resource.expiry_date.isoformat() if resource.expiry_date else None,
                'min_threshold': resource.min_threshold,
                'is_active': resource.is_active,
                'created_at': resource.created_at.isoformat() if resource.created_at else None,
                'updated_at': resource.updated_at.isoformat() if resource.updated_at else None
            })
        
        return jsonify({
            'resources': resources_data,
            'total': resources.total,
            'pages': resources.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching resources'}), 500

@resources_bp.route('/', methods=['POST'])
@jwt_required()
def create_resource():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admin can create resources
        if user.role != 'admin':
            return jsonify({'error': 'Access denied. Admin role required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'resource_type', 'total_quantity', 'min_threshold']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate resource type
        if data['resource_type'] not in ['bed', 'medicine', 'equipment']:
            return jsonify({'error': 'Invalid resource type. Must be bed, medicine, or equipment'}), 400
        
        # Create resource
        resource = Resource(
            name=data['name'],
            resource_type=data['resource_type'],
            category=data.get('category', ''),
            total_quantity=data['total_quantity'],
            available_quantity=data.get('available_quantity', data['total_quantity']),
            unit=data.get('unit', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            min_threshold=data['min_threshold'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify({
            'message': 'Resource created successfully',
            'resource_id': resource.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating resource'}), 500

@resources_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_resource_alerts():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admin can access resource alerts
        if user.role != 'admin':
            return jsonify({'error': 'Access denied. Admin role required'}), 403
        
        # Get low stock resources
        low_stock_resources = Resource.query.filter(
            Resource.available_quantity <= Resource.min_threshold,
            Resource.is_active == True
        ).all()
        
        # Get expired medicines
        expired_medicines = Resource.query.filter(
            Resource.resource_type == 'medicine',
            Resource.expiry_date < date.today(),
            Resource.is_active == True
        ).all()
        
        alerts = []
        
        for resource in low_stock_resources:
            alerts.append({
                'type': 'low_stock',
                'resource_id': resource.id,
                'resource_name': resource.name,
                'available_quantity': resource.available_quantity,
                'min_threshold': resource.min_threshold,
                'priority': 'high' if resource.available_quantity == 0 else 'medium'
            })
        
        for medicine in expired_medicines:
            alerts.append({
                'type': 'expired',
                'resource_id': medicine.id,
                'resource_name': medicine.name,
                'expiry_date': medicine.expiry_date.isoformat(),
                'priority': 'high'
            })
        
        return jsonify({'alerts': alerts}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching resource alerts'}), 500
