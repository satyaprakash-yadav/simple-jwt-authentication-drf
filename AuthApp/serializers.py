from rest_framework import serializers
from AuthApp.models import User
from AuthApp.utils import Util

from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class SignUpSerializer(serializers.ModelSerializer):
    # we are writing this because we need confirm password field in our SignUp Request
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model=User
        fields=["email", "name", "password", "password2", "tc"]
        extra_kwargs={
            "password":{"write_only":True}
        }

    # Validating Password and Confirm Password while SignUp
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError("password and confirm password doesn't match!")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model=User
        fields=["email", "password"]


class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=["id", "email", "name", "tc"]


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)

    class Meta:
        model=User
        fields=["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("password and confirm password doesn't match!")

        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model=User
        fields = ["email"] 

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID :", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("Password Reset Token :", token)
            link = 'http://localhost:3000/api/user/reset/'+uid+"/"+token
            print("Password Reset Link :", link)
            # todo: send email
            body = "Click following link to reset your password - "+ link
            data = {
                "subject": "Reset Your Password",
                "body": body,
                "to_email": user.email
            }
            Util.send_email(data)
            return attrs

        else:
            raise ValidationErr("You are not a SignUp User!")


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)

    class Meta:
        model=User
        fields=["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")

            if password != password2:
                raise serializers.ValidationError("password and confirm password doesn't match!")

            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("Token is not valid or expired!")

            user.set_password(password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError("Token is not valid or expired!")


