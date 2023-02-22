import os
import time

from TeamViewerIoTPythonSDK import TVCMI_client, CertOverrideMode

# sensor id
sensor_id = "dab1aa9062064acbacb5de288edf952e"

# message containing metricId-s to delete
msg = "{\"metrics\": [{\"metricId\" : \"4046926a08c04f4f9edfc8e2ed0e2d83\" }," \
    "{\"metricId\" : \"b8f902710a77443b97a17031f6d9567e\" }] }"

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
    # delete metrics
    client.delete_metric(msg, sensor_id)
    print("metrics deleted")


client.on_api_connect = on_connect
client.connect_api()
while not not_completed:
    time.sleep(1)