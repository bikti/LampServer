from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import  status
from rest_framework.response import Response
from collections import namedtuple
from django.http import JsonResponse

from .serializers import DeviceSerializer
from .models import Device

import serial
from serial.tools import list_ports  # Теперь эта строка должна работать


nt = namedtuple("object", ["model", "serializers"])
pattern = {
    "expense"  : nt(Device, DeviceSerializer),

}
    
@api_view(["GET"])
def BookViewSet(request):
    object =  pattern.get("expense", None)
    if (object == None):
         return JsonResponse(
                 ({'message': 'error'}),
                status = status.HTTP_404_NOT_FOUND
            )
    else:
        object_list = object.model.objects
        serializers  = object.serializers(object_list, many=True)
        return Response(
                data   = serializers.data,
                status = status.HTTP_200_OK
        )
    
@api_view(["GET"])
def get_serial_ports(request):
    """Получить список доступных COM портов"""
    ports = list_ports.comports()
    print("\nДоступные COM-порты:")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device} - {port.description}")
    return JsonResponse({'ports':port.device})
