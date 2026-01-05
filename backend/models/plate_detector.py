"""
Number Plate Detection and OCR Module
Uses YOLOv8 for detection and EasyOCR for text recognition
"""

import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
import logging
from typing import Tuple, List, Dict, Optional
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateDetector:
    """
    Detects vehicle number plates and extracts text using YOLOv8 and EasyOCR
    """
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        ocr_languages: List[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize the PlateDetector with YOLOv8 model and EasyOCR reader
        
        Args:
            model_path: Path to YOLOv8 model weights or model name
            confidence_threshold: Confidence threshold for YOLO predictions
            ocr_languages: Languages for OCR (default: ['en'])
            device: Device to use ('cpu' or 'cuda')
        """
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.ocr_languages = ocr_languages or ['en']
        
        try:
            # Load YOLOv8 model
            logger.info(f"Loading YOLOv8 model from {model_path}")
            self.yolo_model = YOLO(model_path)
            self.yolo_model.to(device)
            
            # Initialize EasyOCR reader
            logger.info(f"Initializing EasyOCR reader for languages: {self.ocr_languages}")
            self.ocr_reader = easyocr.Reader(self.ocr_languages, gpu=(device == 'cuda'))
            
            logger.info("PlateDetector initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PlateDetector: {str(e)}")
            raise
    
    def detect_plates(self, image_path: str) -> List[Dict]:
        """
        Detect number plates in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detected plates with coordinates and confidence scores
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                raise ValueError(f"Invalid image path: {image_path}")
            
            logger.info(f"Processing image: {image_path}")
            
            # Run YOLO detection
            results = self.yolo_model(image, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            if results and len(results) > 0:
                result = results[0]
                
                # Extract detections
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        detection = {
                            'coordinates': {
                                'x1': x1,
                                'y1': y1,
                                'x2': x2,
                                'y2': y2
                            },
                            'confidence': confidence,
                            'class_id': class_id,
                            'width': x2 - x1,
                            'height': y2 - y1
                        }
                        detections.append(detection)
            
            logger.info(f"Detected {len(detections)} plate(s)")
            return detections
            
        except Exception as e:
            logger.error(f"Error in plate detection: {str(e)}")
            raise
    
    def extract_plate_text(self, image_path: str, coordinates: Dict) -> str:
        """
        Extract text from a detected plate region using OCR
        
        Args:
            image_path: Path to the image file
            coordinates: Dictionary containing x1, y1, x2, y2 coordinates
            
        Returns:
            Extracted text from the number plate
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                raise ValueError(f"Invalid image path: {image_path}")
            
            # Extract plate region
            x1 = coordinates['x1']
            y1 = coordinates['y1']
            x2 = coordinates['x2']
            y2 = coordinates['y2']
            
            plate_region = image[y1:y2, x1:x2]
            
            if plate_region.size == 0:
                logger.warning("Empty plate region extracted")
                return ""
            
            # Perform OCR
            results = self.ocr_reader.readtext(plate_region)
            
            # Extract and clean text
            extracted_text = ""
            if results:
                extracted_text = " ".join([text[1] for text in results])
                extracted_text = extracted_text.strip()
            
            logger.info(f"Extracted text: {extracted_text}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            raise
    
    def process_image(self, image_path: str) -> List[Dict]:
        """
        Complete pipeline: detect plates and extract text
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of plates with detected coordinates and extracted text
        """
        try:
            logger.info(f"Starting complete processing for: {image_path}")
            
            # Detect plates
            detections = self.detect_plates(image_path)
            
            # Extract text from each detected plate
            results = []
            for idx, detection in enumerate(detections):
                coordinates = detection['coordinates']
                text = self.extract_plate_text(image_path, coordinates)
                
                result = {
                    'plate_id': idx,
                    'coordinates': coordinates,
                    'confidence': detection['confidence'],
                    'plate_text': text,
                    'dimensions': {
                        'width': detection['width'],
                        'height': detection['height']
                    }
                }
                results.append(result)
            
            logger.info(f"Completed processing: {len(results)} plate(s) detected and processed")
            return results
            
        except Exception as e:
            logger.error(f"Error in image processing: {str(e)}")
            raise
    
    def visualize_detections(
        self,
        image_path: str,
        detections: List[Dict],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Visualize detected plates on the image
        
        Args:
            image_path: Path to the image file
            detections: List of detections from process_image()
            output_path: Optional path to save the visualization
            
        Returns:
            Image array with drawn bounding boxes and text
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                raise ValueError(f"Invalid image path: {image_path}")
            
            image_copy = image.copy()
            
            # Draw bounding boxes and text
            for detection in detections:
                coords = detection['coordinates']
                x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
                text = detection.get('plate_text', 'Unknown')
                confidence = detection['confidence']
                
                # Draw rectangle
                cv2.rectangle(image_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{text} ({confidence:.2f})"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                cv2.rectangle(
                    image_copy,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    (0, 255, 0),
                    -1
                )
                cv2.putText(
                    image_copy,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    1
                )
            
            # Save if output path provided
            if output_path:
                cv2.imwrite(output_path, image_copy)
                logger.info(f"Visualization saved to: {output_path}")
            
            return image_copy
            
        except Exception as e:
            logger.error(f"Error in visualization: {str(e)}")
            raise
    
    def batch_process(self, image_dir: str) -> List[Dict]:
        """
        Process multiple images from a directory
        
        Args:
            image_dir: Directory containing images
            
        Returns:
            List of processing results for all images
        """
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            image_files = [
                f for f in os.listdir(image_dir)
                if Path(f).suffix.lower() in image_extensions
            ]
            
            logger.info(f"Found {len(image_files)} images in {image_dir}")
            
            batch_results = []
            for image_file in image_files:
                image_path = os.path.join(image_dir, image_file)
                try:
                    results = self.process_image(image_path)
                    batch_results.append({
                        'image_file': image_file,
                        'detections': results,
                        'status': 'success'
                    })
                except Exception as e:
                    logger.error(f"Error processing {image_file}: {str(e)}")
                    batch_results.append({
                        'image_file': image_file,
                        'error': str(e),
                        'status': 'failed'
                    })
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise


# Utility functions

def clean_plate_text(text: str) -> str:
    """
    Clean and normalize extracted plate text
    
    Args:
        text: Raw OCR output text
        
    Returns:
        Cleaned text
    """
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Convert to uppercase
    text = text.upper()
    
    # Remove special characters except common ones in plates
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -')
    text = ''.join(c for c in text if c in allowed_chars)
    
    return text.strip()


def validate_plate_format(text: str, country: str = 'IN') -> bool:
    """
    Validate if extracted text matches number plate format
    
    Args:
        text: Extracted plate text
        country: Country code (default: 'IN' for India)
        
    Returns:
        True if valid format, False otherwise
    """
    text = text.strip()
    
    if country == 'IN':
        # Indian plate format: XX-12-AB-1234 or similar variations
        # Should contain digits and letters
        if len(text) < 8:
            return False
        
        has_digits = any(c.isdigit() for c in text)
        has_letters = any(c.isalpha() for c in text)
        
        return has_digits and has_letters
    
    return len(text) > 0


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Number Plate Detection")
    parser.add_argument("--image", type=str, help="Path to image file")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLO model path")
    parser.add_argument("--output", type=str, help="Output path for visualization")
    
    args = parser.parse_args()
    
    if args.image:
        try:
            detector = PlateDetector(model_path=args.model)
            results = detector.process_image(args.image)
            
            print("\n=== Detection Results ===")
            for result in results:
                print(f"Plate {result['plate_id']}:")
                print(f"  Text: {result['plate_text']}")
                print(f"  Confidence: {result['confidence']:.2f}")
                print(f"  Coordinates: {result['coordinates']}")
            
            if args.output:
                detector.visualize_detections(args.image, results, args.output)
        except Exception as e:
            print(f"Error: {str(e)}")
