import time

__RESPONSE_API_CONNECT = "api"
__RESPONSE_PING_SUCESS = "ping"
__MQTT_RESPONSES = {}
__CON_CHECK_TIMEOUTE_SEC = 5

def is_certificate_valid(json_config):
    try:
        from .TVCMI_client import TVCMI_client
        client = TVCMI_client(json_config)
        client.on_api_connect = __on_api_connect
        client.connect_api()
        current_time = __current_time_in_seconds()
        while __RESPONSE_API_CONNECT not in __MQTT_RESPONSES and  __current_time_in_seconds()-current_time < __CON_CHECK_TIMEOUTE_SEC:
            pass
        if __RESPONSE_API_CONNECT not in __MQTT_RESPONSES:
            return False
        __MQTT_RESPONSES.pop(__RESPONSE_API_CONNECT)
        client.on_api_response = __on_connection_check
        client.check_connection()
        current_time = __current_time_in_seconds()
        while __RESPONSE_PING_SUCESS not in __MQTT_RESPONSES and __current_time_in_seconds()-current_time < __CON_CHECK_TIMEOUTE_SEC:
            pass
        return __RESPONSE_PING_SUCESS in __MQTT_RESPONSES
    except:
        return False 

def __on_api_connect(**kwargs):
    __MQTT_RESPONSES[__RESPONSE_API_CONNECT] = True


def __on_connection_check(**kwargs):
    __MQTT_RESPONSES[__RESPONSE_PING_SUCESS] = True

def __current_time_in_seconds():
    return int(round(time.time()))
