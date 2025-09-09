import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    return len(password) >= 8

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def validate_date(date_string, date_format='%Y-%m-%d'):
    """Validate date format"""
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def validate_role(role):
    """Validate user role"""
    return role in ['patient', 'doctor', 'admin']

def validate_gender(gender):
    """Validate gender"""
    return gender in ['male', 'female', 'other']

def validate_resource_type(resource_type):
    """Validate resource type"""
    return resource_type in ['bed', 'medicine', 'equipment']

def validate_appointment_status(status):
    """Validate appointment status"""
    return status in ['scheduled', 'confirmed', 'cancelled', 'completed', 'no_show']
