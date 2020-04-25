import json
import traceback
import zlib

import numpy as np
import dateutil.parser as dt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from fuzzy_extractor import FuzzyExtractor
from kyd_app.models import Device, User
from kyd_app.serializers import DeviceSerializer, AddressSerializer, UserSerializer, DeviceReturnSerializer


class RegisterUser(APIView):
    # Processes a user registration request.
    def post(self, request):
        # Creates user object from the data in the request body.
        birth_date = dt.parse(request.data['birthDate']).strftime("%Y-%m-%d")
        User.objects.create_user(
            username=request.data['account'],
            contract=request.data['contract'],
            first_name=request.data['firstName'],
            last_name=request.data['lastName'],
            birth_date=birth_date,
            email=request.data['email'],
            mobile_number=request.data['mobileNumber']
        )

        # Creates address object from the data in the request body.
        address_serializer = AddressSerializer(data={
            "user": request.data['account'],
            "street": request.data['street'],
            "postal_code": request.data['postalCode'],
            "city": request.data['city'],
            "country": request.data['country'],
        })

        # Serializes the address object and saves it in the database.
        if address_serializer.is_valid():
            address_serializer.save()
        else:
            return Response(
                data=address_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data='',
            status=status.HTTP_201_CREATED
        )


class GetUser(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(username=user_id)
            serializer = UserSerializer(user)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)


class CreateDevice(APIView):
    # Processes a device creation request.
    def post(self, request):
        try:
            # Generates a unique key and the corresponding helper.
            puf_data = bytes.fromhex(request.data['pufData'])
            extractor = FuzzyExtractor(32, 8)
            key, helper = extractor.generate(puf_data)

            # Creates device object from the data in the request body.
            helper_string = json.dumps((
                hex_list(helper[0]),
                hex_list(helper[1]),
                hex_list(helper[2]),
            ))
            id_num = hex(zlib.crc32(key))
            device = {
                "id": id_num,
                "model": request.data['model'],
                "key": key.hex(),
                "helper": helper_string
            }

            # Serializes the device object and saves it in the database.
            serializer = DeviceSerializer(data=device)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            return Response(
                data=traceback.format_exc(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterDevice(APIView):
    # Processes a device registration request.
    def patch(self, request):
        try:
            device = Device.objects.get(id=request.data['id'])
            if not device:
                return Response(status=status.HTTP_204_NO_CONTENT)

            device.name = request.data['name']
            device.account = request.data['account']
            device.contract = request.data['contract']
            device.save()

            return Response(status=status.HTTP_200_OK)
        except:
            return Response(
                data=traceback.format_exc(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetDevice(APIView):
    def get(self, request, device_id):
        try:
            device = Device.objects.get(id=device_id)
            if not device:
                return Response(status=status.HTTP_204_NO_CONTENT)

            serializer = DeviceReturnSerializer(device)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                data=traceback.format_exc(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetDevicesByUser(APIView):
    def get(self, request, user_id):
        try:
            devices = Device.objects.filter(account=user_id)
            if not devices:
                return Response(status=status.HTTP_204_NO_CONTENT)

            serializer = DeviceReturnSerializer(devices, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                data=traceback.format_exc(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyDevice(APIView):
    def post(self, request):
        try:
            id_num = request.data['id']
            try:
                key = Device.objects.get(id=id_num).key
                helper_json = json.loads(Device.objects.get(id=id_num).helper)
            except:
                return Response(
                    data=traceback.format_exc(),
                    status=status.HTTP_404_NOT_FOUND
                )

            helper = (
                np.array(bytes_list(helper_json[0]), dtype='uint8'),
                np.array(bytes_list(helper_json[1]), dtype='uint8'),
                np.array(bytes_list(helper_json[2]), dtype='uint8'),
            )
            extractor = FuzzyExtractor(32, 8)
            puf_data = bytes.fromhex(request.data['pufData'])
            r_key = extractor.reproduce(puf_data, helper)

            if r_key and key == r_key.hex():
                return Response(
                    data='true',
                    status=status.HTTP_200_OK
                )
            return Response(
                data='false',
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                data=traceback.format_exc(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def hex_list(helper_list):
    result = []
    for array in helper_list:
        hex_rep = bytes(array).hex()
        result.append(hex_rep)
    return result


def bytes_list(helper_list):
    result = []
    for string in helper_list:
        bytes_rep = bytes.fromhex(string)
        result.append(list(bytes_rep))
    return result
