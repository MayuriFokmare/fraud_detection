from rest_framework import serializers
from .models import FraudPrediction

class FraudPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudPrediction
        fields = "__all__"

class FraudPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudPrediction
        fields = "__all__"