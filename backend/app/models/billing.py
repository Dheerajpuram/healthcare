from app import db
from datetime import datetime
from decimal import Decimal

class Billing(db.Model):
    __tablename__ = 'billing'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    consultation_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    additional_charges = db.Column(db.Numeric(10, 2), default=0.00)
    discount = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.Enum('pending', 'paid', 'cancelled', 'refunded'), 
                      default='pending', nullable=False)
    payment_method = db.Column(db.Enum('cash', 'card', 'insurance', 'online'), nullable=True)
    payment_reference = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('User', backref='billing_records')
    
    def calculate_total(self):
        self.total_amount = self.consultation_fee + self.additional_charges + self.tax_amount - self.discount
        return self.total_amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'total_amount': float(self.total_amount),
            'consultation_fee': float(self.consultation_fee),
            'additional_charges': float(self.additional_charges),
            'discount': float(self.discount),
            'tax_amount': float(self.tax_amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Billing {self.id}: ${self.total_amount}>'
