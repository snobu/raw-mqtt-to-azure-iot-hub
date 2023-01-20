# Raw MQTT to Azure IoT Hub (in Python) without device SDK

![MQTT logotype](mqtt.png)

A simulated device that implements cloud-to-device and device-to-cloud messaging as well as direct methods over MQTT without using the Azure IoT Device SDK.

This project is using Paho to talk MQTT to Azure IoT Hub.

# WARNING
EVERYTHING HERE IS HIGHLY EXPERIMENTAL.

## Generate the SAS token with azure-cli

First, install the Azure IoT extension: https://github.com/azure/azure-iot-cli-extension#installation

Then generate the SAS key:
```
az iot hub generate-sas-token \
    --hub-name YOUR_IOT_HUB_NAME \
    --device-id YOUR_DEVICE_ID \
    --key-type primary \
    --duration 3600 \
    --output tsv
```

Place the SAS key into a file named `sas.token`.

You'll most probably want a virtual environment first -
https://docs.python.org/3/library/venv.html

Target Python 3.6+.

Run the thing (activate the venv first if using one):
```
$ python run.py
```

## Send cloud to device message
```
az iot device c2d-message send \
    --hub-name poorlyfundedskynet \
    --device-id yolo --data \
    '{"hey device": "this is a cloud to device message"}'
```

## Invoke direct method
```
az iot hub invoke-device-method \
    --hub-name poorlyfundedskynet \
    --device-id yolo \
    --method-name hey \
    --method-payload '{"hey device": "this is a direct method invocation"}'
```

## KNOWN ISSUES
> _Hey, Python is caveman simple, you should rewrite this in C, the language real people use for IoT._

![](https://media.giphy.com/media/11QrDH2UmehokM/giphy.gif)