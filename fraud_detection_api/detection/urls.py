from django.urls import path
from .views import FraudAnalysisView, MerchantFraudSummaryView, FraudPredictionTempSummaryView, FraudByCapturedTextView, FraudDetectionUploadView, FraudPredictionTempClearView, FraudDetectionBatchView

urlpatterns = [
    path("predict/<str:fraud_type>/<str:view_type>/", FraudAnalysisView.as_view(), name="fraud-analysis"),
    path("predict-upload/", FraudDetectionUploadView.as_view(), name="fraud-upload"),
    path("predict-batch/<str:fraud_type>/", FraudDetectionBatchView.as_view(), name="predict-batch"),
    path("clear-temp/", FraudPredictionTempClearView.as_view(), name="clear-temp"),
    path("temp-summary/", FraudPredictionTempSummaryView.as_view(), name="temp-summary"),
    path("temp-category/", FraudByCapturedTextView.as_view(), name="temp-summary"),
    path("merchant-fraud-summary/", MerchantFraudSummaryView.as_view(), name="merchant-fraud-summary"),
]