from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from detection.services.fraud_service import FraudService
from .models import FraudPrediction, FraudPredictionTemp
from .serializers import FraudPredictionSerializer
from django.utils import timezone
from .utils import get_next_transaction_number, clean_for_json
import json
import numpy as np
from . import features as fe
from rest_framework import status
from django.db.models import Count, Q


class FraudAnalysisView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, fraud_type, view_type):
        """
        POST API:
        - Upload CSV file
        - fraud_type: fake_review, payment, chargeback, merchant
        - view_type: summary, breakdown, probabilities
        """
        df = pd.read_csv(request.FILES['file'])

        service = FraudService(fraud_type, model_name="random_forest")  
        df_pred = service.predict(df)

        # Handle tuple returns (model, df)
        if isinstance(df_pred, tuple):
            df_pred = df_pred[1]

        result = service.generate_report(df_pred, view_type)
        return Response(result)

class FraudDetectionBatchView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, fraud_type):
        """
        POST API:
        - Upload CSV file
        - Runs predictions using RandomForest, Logistic Regression, XGBoost
        - Saves all predictions in DB
        - Returns results grouped per record
        """
        file_obj = request.FILES['file']
        df = pd.read_csv(file_obj)

        available_models = ["random_forest", "log_reg", "xgboost"]
        results = []
        records = []

        for _, row in df.iterrows():
            record_dict = {
                "id": None,
                "fraud_type": fraud_type,
                "input_data": row.to_dict(),
                "created_at": timezone.now().isoformat()
            }

            # One DB row for all models
            fraud_prediction = FraudPrediction(
                fraud_type=fraud_type,
                input_data=row.to_dict()
            )

            for model_name in available_models:
                service = FraudService(fraud_type, model_name=model_name)
                prediction_result = service.predict(pd.DataFrame([row]))

                if isinstance(prediction_result, tuple):
                    df_with_results = prediction_result[1]
                else:
                    df_with_results = prediction_result

                pred_row = df_with_results.iloc[0]
                pred_value = bool(pred_row["fraud_prediction"])
                prob_value = float(pred_row["fraud_probability"])

                # Add to API response
                record_dict[model_name] = pred_value
                record_dict[f"{model_name}_probability"] = prob_value

                # Add to DB row
                setattr(fraud_prediction, model_name, pred_value)
                setattr(fraud_prediction, f"{model_name}_probability", prob_value)

            records.append(fraud_prediction)
            results.append(record_dict)

        FraudPrediction.objects.bulk_create(records)

        return Response({
            "fraud_type": fraud_type,
            "total_records": len(results),
            "results": results
        })
    
class FraudDetectionUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        POST API:
        - Upload CSV file
        - Runs predictions using RandomForest, Logistic Regression, XGBoost
        - Saves results in DB
        - Returns results grouped per record with transaction IDs and overall flag
        """
        fraud_type = request.data.get("fraud_type")
        file_obj = request.FILES['file']
        df = pd.read_csv(file_obj)

        df = fe.engineer(df)

        merchant_name_from_request = request.data.get("merchant_name", None)
        available_models = ["random_forest", "log_reg", "xgboost"]

        records, responses = [], []
        next_txn_number = get_next_transaction_number()

        for _, row in df.iterrows():
            txn_id = f"txn{next_txn_number}"
            next_txn_number += 1

            clean_input_data = clean_for_json(row.to_dict())

            # One DB row per record (with all models attached)
            fraud_prediction = FraudPrediction(
                fraud_type=fraud_type,
                transaction_id=txn_id,
                input_data=clean_input_data,
                merchant_name=merchant_name_from_request or row.get("merchant_name"),
            )

            response_record = {
                "transaction_id": txn_id,
                "merchant_name": fraud_prediction.merchant_name,
                "fraud_type": fraud_type,
            }

            if fraud_type == "fake_review":
                response_record["text"] = row.get("text_", None)
                fraud_prediction.captured_text = row.get("text_", None)
            elif fraud_type == "payment":
                response_record["text"] = row.get("Product Category", None)
                fraud_prediction.captured_text = row.get("Product Category", None)
            elif fraud_type == "merchant":
                response_record["text"] = row.get("Issuer organization", None)
                fraud_prediction.captured_text = row.get("Issuer organization", None)
            elif fraud_type == "chargeback":
                response_record["text"] = row.get("Card Number", None)
                fraud_prediction.captured_text = row.get("Card Number", None)

            # predictions for each model
            for model_name in available_models:
                service = FraudService(fraud_type, model_name=model_name)
                _, df_pred = service.predict(pd.DataFrame([row]))
                pred_row = df_pred.iloc[0]

                pred_value = bool(pred_row["fraud_prediction"])
                prob_value = float(pred_row["fraud_probability"])

                # Save to response
                response_record[model_name] = {
                    "status": pred_value,
                    "probability": prob_value
                }

                # Save to DB row
                setattr(fraud_prediction, model_name, pred_value)
                setattr(fraud_prediction, f"{model_name}_probability", prob_value)

                # RandomForest as base
                if model_name == "random_forest":
                    fraud_prediction.status = pred_value
                    response_record["flag"] = pred_value

            records.append(fraud_prediction)
            responses.append(response_record)

        # Bulk save
        FraudPrediction.objects.bulk_create(records)

        # Duplicate objects for temp table
        temp_records = [
            FraudPredictionTemp(
                fraud_type=r.fraud_type,
                input_data=r.input_data,
                transaction_id=r.transaction_id,
                merchant_name=r.merchant_name,
                captured_text=r.captured_text,
                status=r.status,
                random_forest=r.random_forest,
                random_forest_probability=r.random_forest_probability,
                log_reg=r.log_reg,
                log_reg_probability=r.log_reg_probability,
                xgboost=r.xgboost,
                xgboost_probability=r.xgboost_probability,
            )
            for r in records
        ]

        FraudPredictionTemp.objects.bulk_create(temp_records)


        return Response({
            "fraud_type": fraud_type,
            "merchant_name": merchant_name_from_request,
            "total_records": len(records),
            "results": responses
        })
    
class FraudPredictionTempClearView(APIView):
    """
    POST API:
    - Clears all data from fraud_predictions_temp table
    """

    def post(self, request):
        deleted_count, _ = FraudPredictionTemp.objects.all().delete()
        return Response(
            {"message": f"Deleted {deleted_count} records from fraud_predictions_temp"},
            status=status.HTTP_200_OK
        )

class FraudPredictionTempSummaryView(APIView):
    """
    GET API:
    - Returns summary for the unique fraud_type + merchant_name in fraud_predictions_temp
    """

    def get(self, request):
        records = FraudPredictionTemp.objects.all()

        if not records.exists():
            return Response(
                {"message": "No records found in fraud_predictions_temp"},
                status=status.HTTP_200_OK
            )

        fraud_type = records.first().fraud_type
        merchant_name = records.first().merchant_name

        # Counts
        total_count = records.count()
        fraud_count = records.filter(status=True).count()
        non_fraud_count = records.filter(status=False).count()
        fraud_percentage = round((fraud_count / total_count) * 100, 2) if total_count > 0 else 0

        # Transactions list
        transactions = [
            {
                "transaction_id": r.transaction_id,
                "captured_text": r.captured_text,
                "status": "Fraud" if r.status else "Non-fraud"
            }
            for r in records
        ]

        response_data = {
            "fraud_type": fraud_type,
            "merchant_name": merchant_name,
            "total_transactions": total_count,
            "total_fraud": fraud_count,
            "total_non_fraud": non_fraud_count,
            "fraud_percentage": fraud_percentage,
            "transactions": transactions,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class FraudByCapturedTextView(APIView):
    """
    Returns fraud vs non-fraud counts grouped by captured_text (category).
    """

    def get(self, request):
        data = (
            FraudPredictionTemp.objects
            .values("captured_text")
            .annotate(
                total=Count("id"),
                fraud=Count("id", filter=Q(status=True)),
                non_fraud=Count("id", filter=Q(status=False))
            )
            .order_by("-total")
        )
        return Response(list(data))
    
class MerchantFraudSummaryView(APIView):
    """
    Returns fraud vs non-fraud summary grouped by fraud_type for a given merchant,
    along with overall totals.
    """

    def get(self, request):
        merchant = request.query_params.get("merchant")
        if not merchant:
            return Response({"error": "merchant query parameter is required"}, status=400)

        data = (
            FraudPrediction.objects
            .filter(merchant_name=merchant)
            .values("fraud_type")
            .annotate(
                total_transactions=Count("id"),
                fraudulent=Count("id", filter=Q(status=True)),
                non_fraudulent=Count("id", filter=Q(status=False))
            )
        )

        fraud_summary = []
        total_transactions = 0
        total_fraudulent = 0
        total_non_fraudulent = 0

        for item in data:
            total = item["total_transactions"]
            fraudulent = item["fraudulent"]
            non_fraudulent = item["non_fraudulent"]

            fraud_percentage = round((fraudulent / total) * 100, 2) if total > 0 else 0

            fraud_summary.append({
                "fraud_type": item["fraud_type"],
                "total_transactions": total,
                "fraudulent": fraudulent,
                "non_fraudulent": non_fraudulent,
                "fraud_percentage": fraud_percentage
            })

            # Accumulate totals
            total_transactions += total
            total_fraudulent += fraudulent
            total_non_fraudulent += non_fraudulent

        return Response({
            "merchant_name": merchant,
            "fraud_summary": fraud_summary,
            "totalTransactions": total_transactions,
            "totalFraudTransactions": total_fraudulent,
            "totalNonFraudTransaction": total_non_fraudulent
        })