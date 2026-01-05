"""
CRUD operations for the vehicle challan system.
Handles database operations for vehicles, violation types, and challans.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from models import Vehicle, ViolationType, Challan, User
from schemas import (
    VehicleCreate, VehicleUpdate,
    ViolationTypeCreate, ViolationTypeUpdate,
    ChallanCreate, ChallanUpdate
)


# ==================== VEHICLE CRUD OPERATIONS ====================

def get_vehicle(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """
    Retrieve a vehicle by ID.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle
        
    Returns:
        Vehicle object or None if not found
    """
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def get_vehicle_by_registration(db: Session, registration_number: str) -> Optional[Vehicle]:
    """
    Retrieve a vehicle by registration number.
    
    Args:
        db: Database session
        registration_number: Vehicle registration number
        
    Returns:
        Vehicle object or None if not found
    """
    return db.query(Vehicle).filter(
        Vehicle.registration_number == registration_number
    ).first()


def get_vehicles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Vehicle]:
    """
    Retrieve a list of vehicles with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        owner_id: Filter by owner ID
        status: Filter by vehicle status
        
    Returns:
        List of Vehicle objects
    """
    query = db.query(Vehicle)
    
    if owner_id:
        query = query.filter(Vehicle.owner_id == owner_id)
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    return query.offset(skip).limit(limit).all()


def create_vehicle(db: Session, vehicle: VehicleCreate, owner_id: int) -> Vehicle:
    """
    Create a new vehicle record.
    
    Args:
        db: Database session
        vehicle: Vehicle data to create
        owner_id: ID of the vehicle owner
        
    Returns:
        Created Vehicle object
    """
    db_vehicle = Vehicle(
        registration_number=vehicle.registration_number,
        vehicle_type=vehicle.vehicle_type,
        owner_id=owner_id,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        color=vehicle.color,
        status=vehicle.status or "active",
        created_at=datetime.utcnow()
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(
    db: Session,
    vehicle_id: int,
    vehicle_update: VehicleUpdate
) -> Optional[Vehicle]:
    """
    Update an existing vehicle record.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle to update
        vehicle_update: Updated vehicle data
        
    Returns:
        Updated Vehicle object or None if not found
    """
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not db_vehicle:
        return None
    
    update_data = vehicle_update.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    """
    Delete a vehicle record.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not db_vehicle:
        return False
    
    db.delete(db_vehicle)
    db.commit()
    return True


# ==================== VIOLATION TYPE CRUD OPERATIONS ====================

def get_violation_type(db: Session, violation_type_id: int) -> Optional[ViolationType]:
    """
    Retrieve a violation type by ID.
    
    Args:
        db: Database session
        violation_type_id: ID of the violation type
        
    Returns:
        ViolationType object or None if not found
    """
    return db.query(ViolationType).filter(ViolationType.id == violation_type_id).first()


def get_violation_type_by_code(db: Session, code: str) -> Optional[ViolationType]:
    """
    Retrieve a violation type by code.
    
    Args:
        db: Database session
        code: Violation code
        
    Returns:
        ViolationType object or None if not found
    """
    return db.query(ViolationType).filter(ViolationType.code == code).first()


def get_violation_types(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None
) -> List[ViolationType]:
    """
    Retrieve a list of violation types with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        severity: Filter by severity level
        
    Returns:
        List of ViolationType objects
    """
    query = db.query(ViolationType)
    
    if severity:
        query = query.filter(ViolationType.severity == severity)
    
    return query.offset(skip).limit(limit).all()


def create_violation_type(db: Session, violation_type: ViolationTypeCreate) -> ViolationType:
    """
    Create a new violation type record.
    
    Args:
        db: Database session
        violation_type: Violation type data to create
        
    Returns:
        Created ViolationType object
    """
    db_violation_type = ViolationType(
        code=violation_type.code,
        description=violation_type.description,
        severity=violation_type.severity,
        fine_amount=violation_type.fine_amount,
        points=violation_type.points or 0,
        created_at=datetime.utcnow()
    )
    db.add(db_violation_type)
    db.commit()
    db.refresh(db_violation_type)
    return db_violation_type


def update_violation_type(
    db: Session,
    violation_type_id: int,
    violation_type_update: ViolationTypeUpdate
) -> Optional[ViolationType]:
    """
    Update an existing violation type record.
    
    Args:
        db: Database session
        violation_type_id: ID of the violation type to update
        violation_type_update: Updated violation type data
        
    Returns:
        Updated ViolationType object or None if not found
    """
    db_violation_type = db.query(ViolationType).filter(
        ViolationType.id == violation_type_id
    ).first()
    
    if not db_violation_type:
        return None
    
    update_data = violation_type_update.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_violation_type, field, value)
    
    db.commit()
    db.refresh(db_violation_type)
    return db_violation_type


def delete_violation_type(db: Session, violation_type_id: int) -> bool:
    """
    Delete a violation type record.
    
    Args:
        db: Database session
        violation_type_id: ID of the violation type to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_violation_type = db.query(ViolationType).filter(
        ViolationType.id == violation_type_id
    ).first()
    
    if not db_violation_type:
        return False
    
    db.delete(db_violation_type)
    db.commit()
    return True


# ==================== CHALLAN CRUD OPERATIONS ====================

def get_challan(db: Session, challan_id: int) -> Optional[Challan]:
    """
    Retrieve a challan by ID.
    
    Args:
        db: Database session
        challan_id: ID of the challan
        
    Returns:
        Challan object or None if not found
    """
    return db.query(Challan).filter(Challan.id == challan_id).first()


def get_challan_by_number(db: Session, challan_number: str) -> Optional[Challan]:
    """
    Retrieve a challan by challan number.
    
    Args:
        db: Database session
        challan_number: Unique challan number
        
    Returns:
        Challan object or None if not found
    """
    return db.query(Challan).filter(Challan.challan_number == challan_number).first()


def get_challans(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    status: Optional[str] = None,
    officer_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[Challan]:
    """
    Retrieve a list of challans with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        vehicle_id: Filter by vehicle ID
        status: Filter by challan status
        officer_id: Filter by traffic officer ID
        date_from: Filter by issued date (from)
        date_to: Filter by issued date (to)
        
    Returns:
        List of Challan objects
    """
    query = db.query(Challan)
    
    if vehicle_id:
        query = query.filter(Challan.vehicle_id == vehicle_id)
    
    if status:
        query = query.filter(Challan.status == status)
    
    if officer_id:
        query = query.filter(Challan.officer_id == officer_id)
    
    if date_from:
        query = query.filter(Challan.issued_date >= date_from)
    
    if date_to:
        query = query.filter(Challan.issued_date <= date_to)
    
    return query.order_by(Challan.issued_date.desc()).offset(skip).limit(limit).all()


def create_challan(
    db: Session,
    challan: ChallanCreate,
    vehicle_id: int,
    officer_id: int
) -> Challan:
    """
    Create a new challan record.
    
    Args:
        db: Database session
        challan: Challan data to create
        vehicle_id: ID of the vehicle
        officer_id: ID of the issuing officer
        
    Returns:
        Created Challan object
    """
    # Generate unique challan number
    challan_number = generate_challan_number(db)
    
    db_challan = Challan(
        challan_number=challan_number,
        vehicle_id=vehicle_id,
        violation_type_id=challan.violation_type_id,
        officer_id=officer_id,
        issued_date=datetime.utcnow(),
        location=challan.location,
        description=challan.description,
        fine_amount=challan.fine_amount,
        status=challan.status or "pending",
        created_at=datetime.utcnow()
    )
    db.add(db_challan)
    db.commit()
    db.refresh(db_challan)
    return db_challan


def update_challan(
    db: Session,
    challan_id: int,
    challan_update: ChallanUpdate
) -> Optional[Challan]:
    """
    Update an existing challan record.
    
    Args:
        db: Database session
        challan_id: ID of the challan to update
        challan_update: Updated challan data
        
    Returns:
        Updated Challan object or None if not found
    """
    db_challan = db.query(Challan).filter(Challan.id == challan_id).first()
    
    if not db_challan:
        return None
    
    update_data = challan_update.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_challan, field, value)
    
    db.commit()
    db.refresh(db_challan)
    return db_challan


def delete_challan(db: Session, challan_id: int) -> bool:
    """
    Delete a challan record.
    
    Args:
        db: Database session
        challan_id: ID of the challan to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_challan = db.query(Challan).filter(Challan.id == challan_id).first()
    
    if not db_challan:
        return False
    
    db.delete(db_challan)
    db.commit()
    return True


# ==================== ANALYTICAL OPERATIONS ====================

def get_vehicle_challans_count(db: Session, vehicle_id: int) -> int:
    """
    Get total number of challans issued for a vehicle.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle
        
    Returns:
        Count of challans
    """
    return db.query(func.count(Challan.id)).filter(
        Challan.vehicle_id == vehicle_id
    ).scalar()


def get_vehicle_total_fine(db: Session, vehicle_id: int) -> float:
    """
    Get total fine amount for a vehicle.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle
        
    Returns:
        Total fine amount
    """
    result = db.query(func.sum(Challan.fine_amount)).filter(
        Challan.vehicle_id == vehicle_id
    ).scalar()
    return result or 0.0


def get_officer_challans_count(db: Session, officer_id: int, days: int = 30) -> int:
    """
    Get number of challans issued by an officer in the last N days.
    
    Args:
        db: Database session
        officer_id: ID of the officer
        days: Number of days to look back
        
    Returns:
        Count of challans
    """
    date_limit = datetime.utcnow() - timedelta(days=days)
    return db.query(func.count(Challan.id)).filter(
        and_(
            Challan.officer_id == officer_id,
            Challan.issued_date >= date_limit
        )
    ).scalar()


def get_violation_type_statistics(db: Session) -> List[dict]:
    """
    Get statistics of violation types (count of challans per type).
    
    Args:
        db: Database session
        
    Returns:
        List of dictionaries with violation type and challan count
    """
    results = db.query(
        ViolationType.code,
        ViolationType.description,
        func.count(Challan.id).label('count')
    ).outerjoin(Challan).group_by(
        ViolationType.id, ViolationType.code, ViolationType.description
    ).all()
    
    return [
        {
            'code': result[0],
            'description': result[1],
            'challan_count': result[2]
        }
        for result in results
    ]


def get_pending_challans(db: Session, limit: int = 50) -> List[Challan]:
    """
    Get pending challans that need action.
    
    Args:
        db: Database session
        limit: Maximum number of records to return
        
    Returns:
        List of pending Challan objects
    """
    return db.query(Challan).filter(
        Challan.status == 'pending'
    ).order_by(Challan.issued_date).limit(limit).all()


def get_paid_challans_count(db: Session, start_date: Optional[datetime] = None) -> int:
    """
    Get count of paid challans.
    
    Args:
        db: Database session
        start_date: Count paid challans from this date onwards
        
    Returns:
        Count of paid challans
    """
    query = db.query(func.count(Challan.id)).filter(Challan.status == 'paid')
    
    if start_date:
        query = query.filter(Challan.issued_date >= start_date)
    
    return query.scalar()


def get_dashboard_statistics(db: Session) -> dict:
    """
    Get overall dashboard statistics.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with system statistics
    """
    total_vehicles = db.query(func.count(Vehicle.id)).scalar()
    total_challans = db.query(func.count(Challan.id)).scalar()
    pending_challans = db.query(func.count(Challan.id)).filter(
        Challan.status == 'pending'
    ).scalar()
    total_revenue = db.query(func.sum(Challan.fine_amount)).filter(
        Challan.status == 'paid'
    ).scalar()
    
    return {
        'total_vehicles': total_vehicles or 0,
        'total_challans': total_challans or 0,
        'pending_challans': pending_challans or 0,
        'total_revenue': total_revenue or 0.0
    }


# ==================== UTILITY FUNCTIONS ====================

def generate_challan_number(db: Session) -> str:
    """
    Generate a unique challan number.
    
    Args:
        db: Database session
        
    Returns:
        Unique challan number in format: CH-YYYYMMDD-XXXXX
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    
    # Get the count of challans created today
    count = db.query(func.count(Challan.id)).filter(
        Challan.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).scalar()
    
    serial = str(count + 1).zfill(5)
    return f"CH-{date_str}-{serial}"


def search_vehicles(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[Vehicle]:
    """
    Search vehicles by registration number, owner name, or make/model.
    
    Args:
        db: Database session
        query: Search query string
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching Vehicle objects
    """
    search_pattern = f"%{query}%"
    
    return db.query(Vehicle).filter(
        or_(
            Vehicle.registration_number.ilike(search_pattern),
            Vehicle.make.ilike(search_pattern),
            Vehicle.model.ilike(search_pattern)
        )
    ).offset(skip).limit(limit).all()


def get_vehicle_with_owner(db: Session, vehicle_id: int) -> Optional[dict]:
    """
    Get vehicle details along with owner information.
    
    Args:
        db: Database session
        vehicle_id: ID of the vehicle
        
    Returns:
        Dictionary with vehicle and owner details or None
    """
    result = db.query(Vehicle, User).join(User).filter(
        Vehicle.id == vehicle_id
    ).first()
    
    if not result:
        return None
    
    vehicle, owner = result
    return {
        'vehicle': vehicle,
        'owner': owner
    }
