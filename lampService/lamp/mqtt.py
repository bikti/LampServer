import paho.mqtt.client as mqtt
from django.conf import settings

# Callback при подключении
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        client.subscribe('django/mqtt')  # подписываемся на тему
    else:
        print('Bad connection. Code:', rc)

# Callback при получении сообщения
def on_message(client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
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