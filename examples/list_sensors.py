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
connector_params = connection_parameters
# Creating a client to connect to TeamViewer IoT Agent
client = TVCMI_client(connector_params)

# check status of provisioning
not_completed = False


# Callback to be called when connecting securely
def on_connect(**kwargs):
    print("Secure connection is established.")
    # Setting the flag
    global not_completed
    not_completed = True
    # list sensors
    client.list_sensors()
    print("sensor list")


# Callback to be called when gets sensors list info
def on_api_response_list_sensors(**kwargs):
    # Obtaining the response message
    message = kwargs.get('msg')
    print(message)


client.on_api_response = on_api_response_list_sensors


client.on_api_connect = on_connect
client.connect_api()
while not not_completed:
    time.sleep(1)