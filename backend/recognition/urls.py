from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('upload/', views.upload_image, name='upload_image'),
    path('history/', views.get_history, name='get_history'),
    path('export-csv/', views.export_csv, name='export_csv'),
]