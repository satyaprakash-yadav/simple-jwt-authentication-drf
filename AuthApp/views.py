from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate

from AuthApp.serializers import SignUpSerializer, SignInSerializer, ProfileSerializer, ChangePasswordSerializer, SendPasswordResetEmailSerializer, PasswordResetSerializer
from AuthApp.renderers import UserRenderer

from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

#
# Creating tokens manually

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignUp(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({"token": token, "success": "User signup successfully!"}, status=status.HTTP_201_CREATED)
    

class SignIn(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({"token": token, "success": "User signin successfully!"}, status=status.HTTP_200_OK)
        
        else:
            return Response({'errors': {'non_field_errors':['email and password is not valid']}}, status=status.HTTP_404_NOT_FOUND)


class Profile(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        return Response({"success": "password changed successfully!"}, status=status.HTTP_200_OK)
        

class SendPasswordResetEmail(APIView):
    renderer_classes = [UserRenderer]
    
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"success": "password reset link send!"}, status=status.HTTP_200_OK)


class PasswordReset(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token):
        serializer = PasswordResetSerializer(data=request.data, context={"uid": uid, "token": token})
        serializer.is_valid(raise_exception=True)
        return Response({"success": "password reset successfully!"}, status=status.HTTP_200_OK)

