import paho.mqtt.client as mqtt
from django.conf import settings
import json

# Callback при подключении
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        client.subscribe('topic/devices')  # подписываемся на тему
    else:
        print('Bad connection. Code:', rc)

# Callback при получении сообщения
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8')
    print(f'Received message on topic: {msg.topic} with payload: {payload_str}')
    if(msg.topic=="topic/devices"): 
        # Парсим JSON
        data = json.loads(payload_str)
        
        # Извлекаем данные
        device_name = data.get('device_name')
        device_model = data.get('device_model')
        serial_number = data.get('device_sn')
        init_device = data.get('device_init')
        print(f'Device: {device_name}, Model: {device_model}, SN: {serial_number} Init: {init_device}')

    # Здесь можно добавить обработку сообщений

# Создаем и настраиваем клиента
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_SERVER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)