from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponse 
from django.views.decorators.csrf import csrf_exempt
from .mqtt import client as mqtt_client

@csrf_exempt
def publish_message(request):
    if request.method == 'GET':
        try:
            #data = json.loads(request.body)

            rc, mid = mqtt_client.publish('django/mqtt', "123")
            return JsonResponse({'code': rc})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': "ds"}, status=400)
    
        
    
