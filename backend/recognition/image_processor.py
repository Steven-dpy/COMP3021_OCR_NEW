import cv2
import numpy as np
import os
from django.conf import settings
from datetime import datetime

class ImageProcessor:
    """Image processing module for blue part detection and preprocessing"""
    def __init__(self):
        # Blue HSV threshold range (adjust as needed)
        self.lower_blue = np.array([100, 100, 100])
        self.upper_blue = np.array([130, 255, 255])
        
        # Create temporary directory
        self.temp_dir = os.path.join(settings.BASE_DIR, '..', 'share')
        os.makedirs(self.temp_dir, exist_ok=True)

    def detect_blue_part(self, image_path):
        """
        Detect and crop blue part region from image
        :param image_path: Original image path
        :return: Cropped part image path, success status
        """
        try:

            # Read image
            with open(image_path, 'rb') as f:
                img_data = f.read()
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return None, False

            # Convert to HSV color space
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Create blue mask
            mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return None, False

            # Find largest contour (assume largest blue area is the target part)
            max_contour = max(contours, key=cv2.contourArea)

            # Get minimum bounding rectangle
            x, y, w, h = cv2.boundingRect(max_contour)

            # Crop part region
            cropped_image = image[y:y+h, x:x+w]

            # Save cropped image
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            cropped_path = os.path.join(self.temp_dir, f'cropped_{timestamp}.jpg')

            print(f"Cropped image saved to: {cropped_path}")

            # Check if save image successfully
            if not cv2.imwrite(cropped_path, cropped_image) or not os.path.exists(cropped_path):
                raise Exception("Cropped image not saved")

            return cropped_path, True

        except Exception as e:
            print(f"Blue part detection failed: {str(e)}")
            return None, False


    def stretch_to_square(self, image_path):
        """将矩形图片拉伸为正方形（宽高相等）"""
        try:
            image = cv2.imread(image_path)

            # 获取原始图像尺寸
            height, width = image.shape[:2]
            
            # 确定正方形的边长（取原始宽高中的最大值）
            square_size = max(width, height)
            
            # 拉伸图像到正方形尺寸
            square_image = cv2.resize(image, (square_size, square_size), interpolation=cv2.INTER_AREA)

            # Save stretched image
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            stretched_path = os.path.join(self.temp_dir, f'stretched_{timestamp}.jpg')

            print(f"Stretched image saved to: {stretched_path}")

            # Check if save image successfully
            if not cv2.imwrite(stretched_path, square_image) or not os.path.exists(stretched_path):
                raise Exception("Stretched image not saved")
            
            return stretched_path, True
        except Exception as e:
            print(f"Stretch to square failed: {str(e)}")
            return None, False


    def preprocess_image(self, image_path):
        """
        Preprocess image to improve OCR accuracy
        :param image_path: Input image path
        :return: Preprocessed image path, success status
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None, False

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            contrast_enhanced = clahe.apply(gray)

            # Gaussian blur for denoising
            blurred = cv2.GaussianBlur(contrast_enhanced, (3, 3), 0)

            # Binarization
            # _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # blurred = gray
            # Transfer to polar coordinate
            h, w = blurred.shape
            center = (w // 2, h // 2)
            max_radius = min(center[0], center[1])
            polar = cv2.warpPolar(
                blurred, 
                (w, max_radius*8),
                center, 
                max_radius, 
                cv2.WARP_POLAR_LINEAR
            )
            polar_rotated = cv2.rotate(polar, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # polar_copy1 = polar_rotated.copy()
            # polar_copy2 = polar_rotated.copy()
            # combined = np.hstack([polar_copy1, polar_rotated, polar_copy2])

            # Save preprocessed image
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            processed_path = os.path.join(self.temp_dir, f'processed_{timestamp}.jpg')
            cv2.imwrite(processed_path, polar_rotated)

            return processed_path, True

        except Exception as e:
            print(f"Image preprocessing failed: {str(e)}")
            return None, False

    def process(self, image_path):
        """
        Full processing flow: blue part detection -> image preprocessing
        :param image_path: Original image path
        :return: Preprocessed image path, success status
        """
        # Detect blue part
        cropped_path, success = self.detect_blue_part(image_path)
        if not success:
            return None, False
        
        # Stretch to square
        stretched_path, success = self.stretch_to_square(cropped_path)
        if not success:
            return None, False
        
        # Preprocess image
        processed_path, success = self.preprocess_image(stretched_path)

        if not success:
            return None, False


        return {
            'cropped_image': cropped_path,
            'stretched_image': stretched_path,
            'processed_image': processed_path,
        }, success

    def cleanup(self):
        """Clean up temporary files"""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Temporary file cleanup failed: {str(e)}")