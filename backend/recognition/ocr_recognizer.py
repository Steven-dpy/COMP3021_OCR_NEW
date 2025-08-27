import os
from paddleocr import PaddleOCR
from datetime import datetime
from django.conf import settings

class OCRRecognizer:
    """OCR recognition module, responsible for recognizing serial numbers from preprocessed images"""
    def __init__(self):

        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False, 
            use_doc_unwarping=False, 
            use_textline_orientation=False
        ) # text detection + text recognition

        # create temp dir
        self.temp_dir = os.path.join(settings.BASE_DIR, '..', 'share')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def recognize(self, image_path):
        """
        Recognize serial number from image
        :param image_path: Preprocessed image path
        :return: Recognition result (serial number, confidence), success status
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            ocr_image_path = os.path.join(self.temp_dir, f'ocr_{timestamp}.jpg')

            # Read image
            data = self.ocr.predict(image_path)
            for res in data:
                res.print()
                res.save_to_img(ocr_image_path)
                res.save_to_json(self.temp_dir)
            
            # Extract recognition results and confidence
            text = []
            confidences = []
            
            if len(data) > 0:
                for i in range(len(data[0]['rec_texts'])):
                    confidence = float(data[0]['rec_scores'][i])
                    text.append(data[0]['rec_texts'][i])
                    confidences.append(confidence)

            print(data)
            print(text)
            print(confidences)

            # If no text is recognized
            if not text:
                return ("", 0.0, ""), False
            
            # Merge text and calculate average confidence


            serial_number = ''.join(text).strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return (serial_number, avg_confidence, ocr_image_path), True
            
        except Exception as e:
            print(f"OCR recognition failed: {str(e)}")
            return ("", 0.0, ""), False