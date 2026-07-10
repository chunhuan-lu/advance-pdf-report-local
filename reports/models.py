from django.db import models


class Report(models.Model):
    """一份报告的完整 JSON 快照，支持历史列表和再编辑。"""
    id = models.CharField(primary_key=True, max_length=64)
    report_type = models.CharField(max_length=20, default='gas')  # gas | smoke | electrical
    reference_id = models.CharField(max_length=200, blank=True, default='')
    property_address = models.CharField(max_length=500, blank=True, default='')
    data = models.JSONField(default=dict)
    pdf_url = models.CharField(max_length=800, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def summary(self):
        return {
            "id": self.id,
            "type": self.report_type,
            "referenceId": self.reference_id,
            "propertyAddress": self.property_address,
            "pdfUrl": self.pdf_url,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
