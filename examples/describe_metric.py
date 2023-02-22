import time

from TeamViewerIoTPythonSDK import TVCMI_client, CertOverrideMode

# sensor id
sensor_id="237a28fd4cf64b21bacee973d3325803"

# metric id to describe
metric_id="9cbe2d49538c40629f34d8530ee4b8da"

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
    # describe metric
    client.describe_metric(metric_id, sensor_id)
    print("metric details")


# Callback to be called when gets metrics info
def on_api_response_describe_metric(**kwargs):
    # Obtaining the response message
    message = kwargs.get('msg')
    print(message)


client.on_api_response=on_api_response_describe_metric
client.on_api_connect = on_connect
client.connect_api()
while not not_completed:
    time.sleep(1)