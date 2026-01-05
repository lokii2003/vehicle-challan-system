"""
Violation Detector Module
Detects traffic violations including helmet, seat belt, and tripling violations
using computer vision and vehicle detection techniques.
"""

from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


class ViolationType(Enum):
    """Enumeration of violation types"""
    HELMET_NOT_WORN = "helmet_not_worn"
    SEAT_BELT_NOT_WORN = "seat_belt_not_worn"
    TRIPLING = "tripling"
    NONE = "none"


@dataclass
class ViolationDetection:
    """Data class for violation detection results"""
    violation_type: ViolationType
    confidence: float
    location: Tuple[int, int, int, int]  # (x1, y1, x2, y2) bounding box
    timestamp: datetime
    vehicle_id: Optional[str] = None
    additional_info: Optional[Dict] = None


class ViolationDetector:
    """
    Detects traffic violations in vehicle images/video frames.
    Specifically targets helmet, seat belt, and tripling violations.
    """

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize the violation detector.
        
        Args:
            confidence_threshold: Minimum confidence score for violation detection (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.violation_history: List[ViolationDetection] = []

    def detect_helmet_violation(
        self,
        frame: any,
        vehicle_region: Tuple[int, int, int, int]
    ) -> Optional[ViolationDetection]:
        """
        Detect if a rider/driver is not wearing a helmet.
        
        Args:
            frame: Image frame or video frame to analyze
            vehicle_region: Bounding box of vehicle region (x1, y1, x2, y2)
            
        Returns:
            ViolationDetection object if violation detected, None otherwise
        """
        # Implementation would use deep learning model
        # to detect head/face and helmet presence
        violation = ViolationDetection(
            violation_type=ViolationType.HELMET_NOT_WORN,
            confidence=0.0,
            location=vehicle_region,
            timestamp=datetime.utcnow()
        )
        return violation if violation.confidence >= self.confidence_threshold else None

    def detect_seat_belt_violation(
        self,
        frame: any,
        vehicle_region: Tuple[int, int, int, int]
    ) -> Optional[ViolationDetection]:
        """
        Detect if occupants are not wearing seat belts.
        
        Args:
            frame: Image frame or video frame to analyze
            vehicle_region: Bounding box of vehicle region (x1, y1, x2, y2)
            
        Returns:
            ViolationDetection object if violation detected, None otherwise
        """
        # Implementation would use deep learning model
        # to detect seat belt presence across occupants
        violation = ViolationDetection(
            violation_type=ViolationType.SEAT_BELT_NOT_WORN,
            confidence=0.0,
            location=vehicle_region,
            timestamp=datetime.utcnow()
        )
        return violation if violation.confidence >= self.confidence_threshold else None

    def detect_tripling_violation(
        self,
        frame: any,
        vehicle_region: Tuple[int, int, int, int]
    ) -> Optional[ViolationDetection]:
        """
        Detect if more than 2 people are riding a two-wheeler (tripling).
        
        Args:
            frame: Image frame or video frame to analyze
            vehicle_region: Bounding box of vehicle region (x1, y1, x2, y2)
            
        Returns:
            ViolationDetection object if violation detected, None otherwise
        """
        # Implementation would use pose detection and person detection
        # to count occupants in a two-wheeler
        violation = ViolationDetection(
            violation_type=ViolationType.TRIPLING,
            confidence=0.0,
            location=vehicle_region,
            timestamp=datetime.utcnow(),
            additional_info={"occupant_count": 0}
        )
        return violation if violation.confidence >= self.confidence_threshold else None

    def detect_all_violations(
        self,
        frame: any,
        vehicle_region: Tuple[int, int, int, int]
    ) -> List[ViolationDetection]:
        """
        Perform comprehensive violation detection on a vehicle region.
        
        Args:
            frame: Image frame or video frame to analyze
            vehicle_region: Bounding box of vehicle region (x1, y1, x2, y2)
            
        Returns:
            List of detected violations
        """
        violations = []

        helmet_violation = self.detect_helmet_violation(frame, vehicle_region)
        if helmet_violation:
            violations.append(helmet_violation)

        seat_belt_violation = self.detect_seat_belt_violation(frame, vehicle_region)
        if seat_belt_violation:
            violations.append(seat_belt_violation)

        tripling_violation = self.detect_tripling_violation(frame, vehicle_region)
        if tripling_violation:
            violations.append(tripling_violation)

        # Log violations to history
        self.violation_history.extend(violations)

        return violations

    def get_violation_severity(self, violation: ViolationDetection) -> str:
        """
        Determine the severity level of a violation.
        
        Args:
            violation: ViolationDetection object
            
        Returns:
            Severity level: "critical", "high", "medium", "low"
        """
        severity_map = {
            ViolationType.HELMET_NOT_WORN: "critical",
            ViolationType.SEAT_BELT_NOT_WORN: "high",
            ViolationType.TRIPLING: "critical",
            ViolationType.NONE: "none"
        }
        return severity_map.get(violation.violation_type, "low")

    def get_violation_fine(self, violation: ViolationType) -> int:
        """
        Get the standard fine amount for a violation type.
        
        Args:
            violation: Type of violation
            
        Returns:
            Fine amount in rupees
        """
        fine_map = {
            ViolationType.HELMET_NOT_WORN: 500,
            ViolationType.SEAT_BELT_NOT_WORN: 1000,
            ViolationType.TRIPLING: 500,
            ViolationType.NONE: 0
        }
        return fine_map.get(violation, 0)

    def clear_history(self) -> None:
        """Clear violation history"""
        self.violation_history.clear()

    def get_history(self) -> List[ViolationDetection]:
        """
        Get violation detection history.
        
        Returns:
            List of all detected violations
        """
        return self.violation_history.copy()

    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold for violation detection.
        
        Args:
            threshold: Confidence threshold value (0-1)
            
        Raises:
            ValueError: If threshold is not between 0 and 1
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        self.confidence_threshold = threshold
