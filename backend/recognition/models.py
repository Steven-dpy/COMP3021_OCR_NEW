from django.db import models
from django.utils import timezone

class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=50, verbose_name="Serial Number")
    confidence = models.FloatField(verbose_name="Recognition Confidence")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Recognition Time")
    image_path = models.CharField(max_length=255, verbose_name="Image Path")
    status = models.CharField(max_length=20, default="success", verbose_name="Recognition Status")
    

    class Meta:
        verbose_name = "Serial Number Recognition Result"
        verbose_name_plural = "Serial Number Recognition Results"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.serial_number} ({self.confidence:.2f})"

    def to_csv(self):
        """Export as CSV format string"""
        return f"{self.timestamp},{self.serial_number},{self.confidence},{self.image_path},{self.status}\n"