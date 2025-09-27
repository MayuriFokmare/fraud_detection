from django.db import models

from django.db import models

class FraudDetectionAdmin(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    fraud_type = models.CharField(max_length=50)
    merchant_name = models.CharField(max_length=100, null=True, blank=True)
    captured_text = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)

    # Model predictions
    random_forest = models.BooleanField(null=True, blank=True)
    random_forest_probability = models.FloatField(null=True, blank=True)

    log_reg = models.BooleanField(null=True, blank=True)
    log_reg_probability = models.FloatField(null=True, blank=True)

    xgboost = models.BooleanField(null=True, blank=True)
    xgboost_probability = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fraud_detection_admin"


class MetrixTable(models.Model):
    fraud_type = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "metrix_table"