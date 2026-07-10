from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from reports import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('api/reports/', views.ReportListCreate.as_view()),
    path('api/reports/<str:report_id>/', views.ReportDetail.as_view()),
    path('api/photos/', views.PhotoUpload.as_view()),
    path('api/generate/', views.GeneratePdf.as_view()),
    path('api/parse-pdf/', views.ParsePdf.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
