from django.db import models

class FraudPrediction(models.Model):
    fraud_type = models.CharField(max_length=50)
    input_data = models.JSONField()

    # Model predictions
    random_forest = models.BooleanField(null=True, blank=True)
    random_forest_probability = models.FloatField(null=True, blank=True)

    log_reg = models.BooleanField(null=True, blank=True)
    log_reg_probability = models.FloatField(null=True, blank=True)

    xgboost = models.BooleanField(null=True, blank=True)
    xgboost_probability = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fraud_predictions"

class FraudPrediction(models.Model):
    fraud_type = models.CharField(max_length=50)
    input_data = models.JSONField()

    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
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
        db_table = "fraud_predictions_new"

class FraudPredictionTemp(models.Model):
    fraud_type = models.CharField(max_length=50)
    input_data = models.JSONField()

    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    merchant_name = models.CharField(max_length=100, null=True, blank=True)
    captured_text = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)

    random_forest = models.BooleanField(null=True, blank=True)
    random_forest_probability = models.FloatField(null=True, blank=True)

    log_reg = models.BooleanField(null=True, blank=True)
    log_reg_probability = models.FloatField(null=True, blank=True)

    xgboost = models.BooleanField(null=True, blank=True)
    xgboost_probability = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fraud_predictions_temp"