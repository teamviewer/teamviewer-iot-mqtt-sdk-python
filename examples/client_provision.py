import os
import time

from TeamViewerIoTPythonSDK import TVCMI_client, CertOverrideMode

client_name = "python_sdk_client"
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
    print("Secure connection is established for the client - " + client.get_connector_id())
    # print(client.get_connector_id())
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
