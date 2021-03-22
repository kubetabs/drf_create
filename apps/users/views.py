from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from common.rest_framework import CustomRenderer
from common.rest_framework import CustomPagination
from .models import User
from .serializers import UserSerializer
from .serializers import ChangePasswordSerializer


class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    # permission_classes = []
    pagination_class = CustomPagination
    renderer_classes = [CustomRenderer]
    permission_classes_by_action = {
        'create': [AllowAny],
    }

    def create(self, request, *args, **kwargs):
        """
        用户注册，不需要权限
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 明文密码加密
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # 明文密码加密
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT, headers=headers)

    @action(detail=True, methods=['post'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not instance.check_password(serializer.data.get('old_password')):
                return Response({"msg": "旧密码错误"}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            instance.set_password(serializer.data.get('new_password'))
            instance.save()
            return Response({"msg": "密码更新成功"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def test(self, request, *args, **kwargs):
        # print(acd)
        raise ValidationError({"detail": "here raise"})
        # return Response("here error", status=status.HTTP_200_OK)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
