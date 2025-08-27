from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
import uuid
from django.conf import settings
from .services import RecognitionService

# Create upload directory
UPLOAD_DIR = os.path.join(settings.BASE_DIR, '..', 'share')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    return Response(data={'message': 123}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def upload_image(request):
    """
    Upload image and perform serial number recognition
    """


    if 'image' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Image file not found'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Save uploaded image
        image_file = request.FILES['image']
        filename = f'{uuid.uuid4()}_{image_file.name}'

        # The file name may contains Chinese, it would be better to encode it.
        filename = filename.encode('utf-8').decode('utf-8')
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        print("Save uploaded image success.")

        # Call recognition service
        recognition_service = RecognitionService()
        print("RecognitionService init success.")
        result, success = recognition_service.process_image(file_path)

        # only keep the file name
        result['cropped_image'] = os.path.basename(result['cropped_image'])
        result['stretched_image'] = os.path.basename(result['stretched_image'])
        result['processed_image'] = os.path.basename(result['processed_image'])
        result['ocr_image'] = os.path.basename(result['ocr_image'])


        print("Process image result", result, success)

        if success:
            return Response({
                    'success': True,
                    'serial_number': result['serial_number'],
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'origin_image': filename,
                    'cropped_image': result['cropped_image'],
                    'stretched_image': result['stretched_image'],
                    'processed_image': result['processed_image'],
                    'ocr_image': result['ocr_image'],
                })

        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error occurred while processing image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_history(request):
    """
    Get recognition history records
    """
    from .models import SerialNumber
    from django.core.paginator import Paginator

    try:
        # Get pagination parameters
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        # Query records
        records = SerialNumber.objects.all().order_by('-timestamp')
        paginator = Paginator(records, page_size)
        current_page = paginator.get_page(page)

        # Format response
        data = {
            'success': True,
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': current_page.number,
            'results': [{
                'id': record.id,
                'serial_number': record.serial_number,
                'confidence': record.confidence,
                'timestamp': record.timestamp.isoformat(),
                'image_path': record.image_path,
                'status': record.status
            } for record in current_page.object_list]
        }

        return Response(data)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to get history records: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_csv(request):
    """
    Export recognition results as CSV file
    """
    try:
        recognition_service = RecognitionService()
        file_path, success = recognition_service.export_to_csv()

        if success:
            # Return CSV file path
            return Response({
                'success': True,
                'csv_path': file_path,
                'message': 'CSV file exported successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'CSV file export failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error occurred while exporting CSV: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
