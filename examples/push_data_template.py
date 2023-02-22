from TeamViewerIoTPythonSDK import TVCMI_client, CertOverrideMode
import time
import random

# parameters to be provided by user
client_name = "UserClient"
sensor_id = "UserSensor"
delay = 1


def get_data(**kwargs):
    # Data in IoT push data format, that user should provide to push to cloud
    # Dummy data, for default case:
    metric_id_1 = "metric1"
    metric_id_2 = "metric2"
    value1 = random.randint(1, 20)
    value2 = random.randint(1, 20)

    metric_data = {"metrics": [{"metricId": metric_id_1, "value": value1},
                               {"metricId": metric_id_2, "value": value2}]}
    return metric_data


def on_certificate_received(**kwargs):
    # Obtaining the response message
    MQTT_RESPONSES[PREFIX_CERTIFICATE_INFO] = "True"


def on_connect(**kwargs):
    MQTT_RESPONSES[PREFIX_API_CONNECTED] = "True"


def on_error(**kwargs):
    pass


def on_push_metric_values(**kwargs):
    pass


def provision_client():
    global client
    global MQTT_RESPONSES
    global PREFIX_FINISHED
    global PREFIX_CERTIFICATE_INFO
    global PREFIX_API_CONNECTED

    MQTT_RESPONSES = {}
    PREFIX_CERTIFICATE_INFO = "certificate_info_"
    PREFIX_API_CONNECTED = "api_connected_"
    PREFIX_FINISHED = "Finished"

    tv_mqtt_configs = {}
    tv_mqtt_configs['ClientName'] = client_name
    tv_mqtt_configs['MqttHost'] = 'localhost'
    tv_mqtt_configs['MqttProvisionPort'] = '18883'
    tv_mqtt_configs['MqttPort'] = '18884'
    tv_mqtt_configs['MqttKeepAlive'] = 'None'
    tv_mqtt_configs['OverrideCerts'] = CertOverrideMode.SMART
    tv_mqtt_configs['CaFile'] = '/var/lib/teamviewer-iot-agent/certs/TeamViewerAuthority.crt'
    tv_mqtt_configs['CertFolder'] = "/var/lib/teamviewer-iot-agent/certs"

    client = TVCMI_client(tv_mqtt_configs)
    client.on_api_response = on_certificate_received
    client.on_api_error = on_error
    client.provision()
    while PREFIX_CERTIFICATE_INFO not in MQTT_RESPONSES:
        pass
    client.on_api_connect = on_connect
    client.connect_api()
    while PREFIX_API_CONNECTED not in MQTT_RESPONSES:
        pass
    MQTT_RESPONSES.pop(PREFIX_API_CONNECTED)
    client.on_api_response = on_push_metric_values
    while True:
        client.push_metrics(sensor_id, get_data())
        time.sleep(delay)
    while PREFIX_FINISHED not in MQTT_RESPONSES:
        pass


provision_client()
