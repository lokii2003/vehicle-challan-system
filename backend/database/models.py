from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class Vehicle(Base):
    """Model representing a vehicle in the system."""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(20), unique=True, index=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # Car, Bike, Truck, etc.
    owner_name = Column(String(255), nullable=False)
    owner_contact = Column(String(20), nullable=False)
    owner_email = Column(String(255), nullable=True)
    owner_address = Column(Text, nullable=True)
    chassis_number = Column(String(50), unique=True, nullable=False)
    engine_number = Column(String(50), unique=True, nullable=False)
    manufacturing_year = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    fuel_type = Column(String(50), nullable=True)  # Petrol, Diesel, Electric, etc.
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    challans = relationship("Challan", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, registration_number={self.registration_number}, owner_name={self.owner_name})>"


class ViolationType(Base):
    """Model representing traffic violation types."""
    __tablename__ = "violation_types"

    id = Column(Integer, primary_key=True, index=True)
    violation_code = Column(String(20), unique=True, index=True, nullable=False)
    violation_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    fine_amount = Column(Float, nullable=False)
    penalty_points = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    challans = relationship("Challan", back_populates="violation_type")

    def __repr__(self):
        return f"<ViolationType(id={self.id}, violation_code={self.violation_code}, violation_name={self.violation_name})>"


class ChallanStatus(enum.Enum):
    """Enumeration for challan status."""
    ISSUED = "issued"
    PAID = "paid"
    PENDING = "pending"
    CANCELLED = "cancelled"
    APPEALED = "appealed"
    RESOLVED = "resolved"


class Challan(Base):
    """Model representing a traffic challan/fine."""
    __tablename__ = "challans"

    id = Column(Integer, primary_key=True, index=True)
    challan_number = Column(String(50), unique=True, index=True, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    violation_type_id = Column(Integer, ForeignKey("violation_types.id"), nullable=False, index=True)
    
    # Violation details
    violation_location = Column(String(255), nullable=False)
    violation_latitude = Column(Float, nullable=True)
    violation_longitude = Column(Float, nullable=True)
    violation_date = Column(DateTime, nullable=False)
    
    # Challan details
    issued_by_officer = Column(String(255), nullable=False)
    officer_id = Column(String(50), nullable=True)
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Fine and payment details
    fine_amount = Column(Float, nullable=False)
    additional_charges = Column(Float, default=0, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(ChallanStatus), default=ChallanStatus.ISSUED, nullable=False, index=True)
    
    # Payment information
    payment_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)  # Online, Offline, etc.
    transaction_id = Column(String(100), nullable=True)
    
    # Additional fields
    remarks = Column(Text, nullable=True)
    appeal_status = Column(String(50), nullable=True)
    appeal_date = Column(DateTime, nullable=True)
    appeal_remarks = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="challans")
    violation_type = relationship("ViolationType", back_populates="challans")

    def __repr__(self):
        return f"<Challan(id={self.id}, challan_number={self.challan_number}, vehicle_id={self.vehicle_id}, status={self.status})>"
