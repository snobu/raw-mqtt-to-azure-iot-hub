import sys
import ssl
import certifi
import time
import json
import re
import paho.mqtt.client as mqtt
from colorama import init
init()
from colorama import Fore, Back, Style

# Generate the SAS token with azure-cli
# https://github.com/azure/azure-iot-cli-extension#installation
# Example: az iot hub generate-sas-token --hub-name YOUR_IOT_HUB_NAME --device-id YOUR_DEVICE_ID --key-type primary --duration 3600
try:
    f = open("sas.token", "r")
    SAS_TOKEN = f.readline()
except FileNotFoundError:
    print('File "sas.token" not found.\nCreate it and place the SAS token on the first line.')
    sys.exit(404)

class DirectMethod:
    name = None
    rid = None

def extract_direct_method(msg):
    direct_method = DirectMethod()
    # Extract method name and request id
    direct_method.name = re.compile('\/POST\/(\w+)').findall(msg.topic)[0]
    direct_method.rid = re.compile('\$rid=(\w+)').findall(msg.topic)[0]

    return direct_method

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    print('Subscribing to device specific message topic...')
    client.subscribe('devices/yolo/messages/devicebound/#')
    print('Subscribing to direct method topic...')
    client.subscribe('$iothub/methods/POST/#')

    # To respond, the device sends a message with a valid JSON or empty body
    # to the topic $iothub/methods/res/{status}/?$rid={request id}.
    # In this message, the request ID must match the one in the request message,
    # and status must be an integer.
     
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # Handle cloud to device messages
    if 'devices/yolo/messages/devicebound/' in msg.topic:
        print(Back.CYAN +
            '*** Received Cloud to Device Message:\n' +
            Style.RESET_ALL +
            f'      Topic: {msg.topic}\n' +
            f'      Payload: {msg.payload}\n')

    # Handle direct methods
    if '$iothub/methods/' in msg.topic:
        direct_method = extract_direct_method(msg)
        print(Back.YELLOW +
            '*** Received Direct Method invocation:\n' +
            Style.RESET_ALL +
            f'            Topic: {msg.topic}\n' +
            f'      Method name: {direct_method.name}\n' +
            f'       Request id: {direct_method.rid}\n')
        # Execute direct method logic then reply with status
        time.sleep(2)
        response_code = 200
        response_payload = {
            'all_good': True,
            'battery': 'good'
        }
        client.publish(f'$iothub/methods/res/{response_code}/?$rid={direct_method.rid}',
            payload=json.dumps(response_payload),
            qos=0,
            retain=False)
        print('Sent direct method response.')
    
    print('Parsing msg.payload -')
    try:
        p = json.loads(str(msg.payload, 'utf-8'))
        payload = json.dumps(p, indent=4)
        print(f'Payload: \n{payload}')
    except:
        print(Fore.RED + 'Unable to deserialize msg.payload as JSON.')
        print(Style.RESET_ALL)

def on_publish(client, userdata, result):
    print("\nData published.\n")

# Always use MQTT v3.1.1 with Azure IoT Hub.
# MQTT v3.1 won't be able to connect at all (Paho error 3 or 5).
client = mqtt.Client(client_id='yolo', clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport='tcp')
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect to Azure IoT Hub
ca_bundle = certifi.where()
print(f'Using CA bundle provided by certifi, version {certifi.__version__}.')
# If you don't specify your own CA bundle PEM file, Python will
# attempt to use the default CA on the system.
client.tls_set(ca_certs=ca_bundle, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(False)
client.username_pw_set(username='poorlyfundedskynet.azure-devices.net/yolo/?api-version=2018-06-30', password=SAS_TOKEN)
#client._ssl_context.load_verify_locations(cafile='badssl.crl.pem')
#client._ssl_context.load_verify_locations(cafile='microsoftca4.crl.pem')
#client._ssl_context.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
client.connect('poorlyfundedskynet.azure-devices.net', 8883, 60)
#client.connect('revoked.badssl.com', 443, 60)
print('------------ TLS session info ----------')
print(client._ssl_context.protocol)
print(client._ssl_context.cert_store_stats())
print('----------------------------------------')

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()
client.loop_start()

SLEEP_DELAY = 500
while True:
    time.sleep(2)
    print('Publishing message to broker..')
    client.publish('devices/yolo/messages/events/', payload=f"hey hey this is yolo at {time.strftime('%Y-%m-%d %H:%M:%S')}", qos=1, retain=False)
    print(f'Sleeping for {SLEEP_DELAY} seconds.')
    time.sleep(SLEEP_DELAY)