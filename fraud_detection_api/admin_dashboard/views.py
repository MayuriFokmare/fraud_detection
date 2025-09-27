from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from detection.models import FraudPrediction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import numpy as np
from detection.services.fraud_service import FraudService

# Fraud summary by type
class FraudTypeSummaryView(APIView):
    """
    Returns fraud vs non-fraud summary grouped by fraud_type.
    """

    def get(self, request):
        data = (
            FraudPrediction.objects
            .values("fraud_type")
            .annotate(
                total_transactions=Count("id"),
                fraudulent=Count("id", filter=Q(status=True)),
                non_fraudulent=Count("id", filter=Q(status=False))
            )
        )
        return Response(list(data))


# Merchant-level fraud stats
class MerchantFraudView(APIView):
    """
    Returns total and fraudulent transaction counts grouped by merchant_name.
    """

    def get(self, request):
        data = (
            FraudPrediction.objects
            .values("merchant_name")
            .annotate(
                total=Count("id"),
                fraudulent=Count("id", filter=Q(status=True))
            )
        )
        return Response(list(data))


#  Detailed fraudulent records
class FraudulentRecordsView(APIView):
    """
    Returns detailed fraudulent records for admin inspection.
    """

    def get(self, request):
        data = (
            FraudPrediction.objects
            .values("transaction_id", "merchant_name", "fraud_type", "captured_text", "status")
        )
        return Response(list(data))