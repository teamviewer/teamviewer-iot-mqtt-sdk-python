import json
import os
import time

from TeamViewerIoTPythonSDK import TVCMI_client, CertOverrideMode

client_name = "python_sdk_client"
sensor_name = "python_sdk_sensor"

cert_path = "/var/lib/teamviewer-iot-agent/certs/"

# Putting connection parameters in JSON
connection_parameters = {}
connection_parameters['ClientName'] = client_name
connection_parameters['MqttHost'] = 'localhost'
connection_parameters['MqttProvisionPort'] = '18883'
connection_parameters['MqttPort'] = '18884'
connection_parameters['MqttKeepAlive'] = 'None'
connection_parameters['OverrideCerts'] = CertOverrideMode.SMART
connection_parameters['CaFile'] = '/var/lib/teamviewer-iot-agent/certs/TeamViewerAuthority.crt'
connection_parameters['CertFolder'] = cert_path

# Storing ID-s
sensor_id = None
metric1_id = None
metric2_id = None

not_completed = False


# Callback to be called when authorized certificate on provisioning is received
def on_certificate_received(**kwargs):
    # Obtaining the response message
    message = kwargs.get('msg')
    print(message)

    global not_completed
    not_completed = True


# Callback to be called when connecting securely
def on_connect(**kwargs):
    print("Secure connection is established.")
    # Setting the callback to receive the sensor ID
    client.on_api_response = on_sensor_created
    # Create a sensor
    client.create_sensor(sensor_name)


# Callback to be called when sensor is created
def on_sensor_created(**kwargs):

    print("Sensor is created.")
    # Retrieving the message received
    message = kwargs.get('msg')
    # Loading the message into a JSON
    message_json = json.loads(message.decode('utf-8'))

    # Retrieving the sensor id
    global sensor_id
    sensor_id = message_json['sensorId']
    # Setting the callback to receive the sensor ID
    client.on_api_response = on_metric_created
    # Defining metric 1
    metric1_parameters = {}
    metric1_parameters['matchingId'] = "1"
    metric1_parameters['name'] = 'metric1_name'
    metric1_parameters['valueAnnotation'] = 'unit1'
    metric1_parameters['valueType'] = 'string'

    # Defining metric 2
    metric2_parameters = {}
    metric2_parameters['matchingId'] = "2"
    metric2_parameters['name'] = 'metric2_name'
    metric2_parameters['valueAnnotation'] = 'unit2'
    metric2_parameters['valueType'] = 'integer'

    # Putting metric 1 and metric 2 into a single container
    metrics_container = {'metrics': [metric1_parameters, metric2_parameters]}
    print(metrics_container)
    # Create a metric
    client.create_metric(metrics_container, sensor_id)


def on_metric_created(**kwargs):
    print("Metrics are created.")
    # Retrieving the message received
    message = kwargs.get('msg')
    # Loading the message into a JSON
    metric_data = json.loads(message.decode('utf-8'))

    # Retrieving the sensor id
    global metric1_id
    metric1_id = metric_data[0]["metricId"]

    global metric2_id
    metric2_id = metric_data[1]["metricId"]
    print("A sensor and two metrics are successfully created.")
    print("Sensor ID is: " + sensor_id)
    print("Metric1 ID is: " + metric1_id)
    print("Metric2 ID is: " + metric2_id)
    global not_completed
    not_completed = True


# Callback to be called when error occurred
def on_error(**kwargs):
    print(kwargs)
    global not_completed
    not_completed = True
    # For detailed info please uncomment this part of code
    # error_str = kwargs.get('error_str')
    # error_code = kwargs.get('error_code')
    # raise TvcmiError(error_code, error_str)

# Callback to be called when log method called in sdk
def on_api_log(msg):
    print(msg)


# Creating a new client to connect to TeamViewer IoT Agent
client = TVCMI_client(connection_parameters)
# Setting a callback to receive an authorized certificate if the client is not provisioned
client.on_api_response = on_certificate_received
# Setting a callback for errors
client.on_api_error = on_error

# Setting a callback for logs on_api_log
client.on_api_log = on_api_log

# Provisioning the client
client.provision()

while not not_completed:
  time.sleep(1)
not_completed = False
# Setting the callback to know when connected
client.on_api_connect = on_connect
# Establishing a secure connection with TeamViewer IoT Agent
client.connect_api()
while not not_completed:
  time.sleep(1)
