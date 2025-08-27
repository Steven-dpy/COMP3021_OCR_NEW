import os
import time
from django.utils import timezone
from .image_processor import ImageProcessor
from .ocr_recognizer import OCRRecognizer
from .models import SerialNumber

class RecognitionService:
    """Recognition service, coordinates image processing and OCR recognition flow"""
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.ocr_recognizer = OCRRecognizer()

    def process_image(self, image_path):
        """
        Full processing flow: image processing -> OCR recognition -> result storage
        :param image_path: Original image path
        :return: Processing result, success status
        """
        start_time = time.time()
        result = {
            'success': False,
            'serial_number': '',
            'confidence': 0.0,
            'processing_time': 0.0,
            'error': None,
            'cropped_image': None,
            'stretched_image': None,
            'processed_image': None,
            'ocr_image': None,

        }

        try:
            # 1. Image processing
            processed_paths, success = self.image_processor.process(image_path)
            print(f"Image processing result: {processed_paths['processed_image']}, {success}")


            if not success:
                result['error'] = 'Image processing failed'
                return result, False

            # 2. OCR recognition
            (serial_number, confidence, ocr_image_path), success = self.ocr_recognizer.recognize(processed_paths['processed_image'])

            print(f"OCR recognition result: {serial_number}, {confidence}, {success}")

            if not success:
                result['error'] = 'OCR recognition failed'
                return result, False

            # 3. Result storage

            print("Saving recognition result...")

            recognition_result = SerialNumber(
                serial_number=serial_number,
                confidence=confidence,  # Convert to 0-1 range
                timestamp=timezone.now(),
                image_path=image_path,
                status='success'
            )
            recognition_result.save()

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update result
            result.update({
                'success': True,
                'serial_number': serial_number,
                'confidence': confidence,
                'processing_time': processing_time,
                'cropped_image': processed_paths['cropped_image'],
                'stretched_image': processed_paths['stretched_image'],
                'processed_image': processed_paths['processed_image'],
                'ocr_image': ocr_image_path,
            })

            print(f"Recognition result: {result}")




            return result, True

        except Exception as e:
            result['error'] = f'Error occurred during processing: {str(e)}'

            print(f"Error occurred during processing: {str(e)}")


            return result, False

    def export_to_csv(self, file_path=None):
        """
        Export all recognition results to a CSV file
        :param file_path: Export path, if None use default path
        :return: Exported file path, success status
        """
        try:
            if not file_path:
                # Default path
                file_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'recognition_results.csv'
                )

            # Get all results
            results = SerialNumber.objects.all().order_by('-timestamp')

            # Write to CSV
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write('timestamp,serial_number,confidence,image_path,status\n')
                # Write data
                for result in results:
                    f.write(result.to_csv())

            return file_path, True

        except Exception as e:
            print(f"CSV export failed: {str(e)}")
            return None, False
