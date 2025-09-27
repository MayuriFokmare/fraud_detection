from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
import secrets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, PasswordResetToken


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'address', 'pincode', 'mobile_no']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            address=validated_data.get('address', ''),
            pincode=validated_data.get('pincode', ''),
            mobile_no=validated_data.get('mobile_no', ''),
            role='MERCHANT',
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['name'] = user.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'name': self.user.name,
                'role': self.user.role,
            }
        })
        return data


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email'].lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        token = secrets.token_hex(32)
        expires_at = timezone.now() + timedelta(minutes=30)
        PasswordResetToken.objects.create(user=user, token=token, expires_at=expires_at)
        return {'user': user, 'token': token}


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        try:
            prt = PasswordResetToken.objects.select_related('user').get(token=attrs['token'])
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")
        if not prt.is_valid():
            raise serializers.ValidationError("Token expired or already used")
        attrs['prt'] = prt
        return attrs

    def create(self, validated_data):
        prt = validated_data['prt']
        user = prt.user
        user.set_password(validated_data['new_password'])
        user.save()
        prt.used = True
        prt.save()
        return user