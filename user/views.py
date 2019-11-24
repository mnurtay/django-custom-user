from django.shortcuts import render
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, views
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import models
from . import serializers


class LoginApiView(views.APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        try:
            serializer = serializers.LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(
                username=serializer.data.get('username'),
                password=serializer.data.get('password'))
            if not user:
                raise ObjectDoesNotExist
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': serializers.UserSerializer(user).data,
                'token': token.key},
                status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'detail': 'Invalid password or username'}, status=status.HTTP_400_BAD_REQUEST)


class SignupApiView(views.APIView):
    serializer_class = serializers.UserSerializer

    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': serializers.UserSerializer(user).data,
            'token': token.key},
            status=status.HTTP_200_OK)


class ResetPasswordApiView(views.APIView):
    serializer_class = serializers.ResetPasswordSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user.check_password(serializer.data.get('old_password')):
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'result': 'Success'})
        return Response({'error': 'Invalid password'})


class UpdateProfileApiView(views.APIView):
    serializer_class = serializers.UpdateProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = serializers.UpdateProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        models.User.objects.filter(pk=request.user.id).update(**serializer.data)
        user = models.User.objects.get(pk=request.user.id)
        return Response({
            'user': serializers.UserSerializer(user).data
        })
