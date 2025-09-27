from django.urls import path
from .views import FraudTypeSummaryView, MerchantFraudView, FraudulentRecordsView

urlpatterns = [
    path("fraud-summary/", FraudTypeSummaryView.as_view(), name="fraud-summary"),
    path("merchant-fraud/", MerchantFraudView.as_view(), name="merchant-fraud"),
    path("fraudulent-records/", FraudulentRecordsView.as_view(), name="fraudulent-records"),
    # path("upload-file/", AdminFileUploadView.as_view(), name="admin-upload-file"),
    # path("metrics-summary/", MetricsSummaryView.as_view(), name="metrics-summary"),
]