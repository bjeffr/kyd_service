from rest_framework import serializers
from kyd_app.models import Device, Address, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'contract', 'first_name', 'last_name', 'birth_date', 'email', 'mobile_number']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'model', 'key', 'helper', 'name', 'account', 'contract']


class DeviceReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'model', 'name', 'contract']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'street', 'postal_code', 'city', 'country']
