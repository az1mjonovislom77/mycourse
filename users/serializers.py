from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import CustomUser
from django.core.exceptions import ValidationError


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Parollar bir xil emas!")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = False 
        user.verification_code = self.generate_verification_code()
        user.save()
        return user

    def generate_verification_code(self):
        import random
        return str(random.randint(100000, 999999))


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")

        if not user.check_password(password):
            raise serializers.ValidationError("Parol noto‘g‘ri")

        return user



class VerifyEmailSerializer(serializers.Serializer):
    verification_code = serializers.CharField()

    def validate(self, attrs):
        verification_code = attrs.get('verification_code')
        user = CustomUser.objects.filter(verification_code=verification_code).first()

        if not user:
            raise serializers.ValidationError("Noto‘g‘ri tasdiqlash kodi")

        return attrs
