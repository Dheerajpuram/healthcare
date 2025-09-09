from app import db
from datetime import datetime

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.Enum('bed', 'medicine', 'equipment'), nullable=False)
    category = db.Column(db.String(50), nullable=True)  # e.g., 'ICU', 'General', 'Pain Relief', 'Surgical'
    total_quantity = db.Column(db.Integer, nullable=False, default=0)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=True)  # e.g., 'beds', 'units', 'mg', 'ml'
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)  # For beds and equipment
    expiry_date = db.Column(db.Date, nullable=True)  # For medicines
    min_threshold = db.Column(db.Integer, default=5)  # Alert when below this quantity
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('ResourceTransaction', backref='resource', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'resource_type': self.resource_type,
            'category': self.category,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'unit': self.unit,
            'description': self.description,
            'location': self.location,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'min_threshold': self.min_threshold,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def is_low_stock(self):
        return self.available_quantity <= self.min_threshold
    
    def __repr__(self):
        return f'<Resource {self.name}: {self.available_quantity}/{self.total_quantity}>'

class ResourceTransaction(db.Model):
    __tablename__ = 'resource_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    transaction_type = db.Column(db.Enum('in', 'out', 'adjustment'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    reference_id = db.Column(db.String(50), nullable=True)  # e.g., appointment_id, purchase_order_id
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'reason': self.reason,
            'reference_id': self.reference_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ResourceTransaction {self.id}: {self.transaction_type} {self.quantity}>'
