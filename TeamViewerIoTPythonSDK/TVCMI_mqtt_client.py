from socket import gaierror
import paho.mqtt.client as paho
from .TVCMI_error import TLSError, ConnectionParamError

import os
import ssl
import json
import re

TVCMI_Callback_ArgumentsMismatch = 20
TVCMI_TLS_Error = 21


class _ProvisionParams:

    def __init__(self, publish_topic=None, subscribe_topic=None, error_topic=None, msg=None, callback=None):
        self.publish_topic = publish_topic
        self.subscribe_topic = subscribe_topic
        self.error_topic = error_topic
        self.msg = msg
        self.callback = callback


class _ConnectNetwork(object):

    def __init__(self, params):

        self.mqtt_client = None
        self.connection_params = params
        self.file_location = params.directory
        self._on_error_callback = None
        self._on_log_callback = None
        self._on_disconnect_callback = None
        self._on_connect_callback = None
        self._on_message_callback = None
        self.user_data = None
        self.provision_params = None
        self.connected = False


    def _create_mqtt_client(self, user_data):
        self.mqtt_client = paho.Client(client_id="", clean_session=True, userdata=user_data, protocol=paho.MQTTv311)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.user_data = None
        self.__logger("SUCCESS: MQTT client is created.")

    def __del__(self):
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            del self.mqtt_client

    @property
    def on_log_callback(self):
        return self._on_log_callback

    @on_log_callback.setter
    def on_log_callback(self, func):
        self._on_log_callback = func

    @property
    def on_error_callback(self):
        return self._on_error_callback

    @on_error_callback.setter
    def on_error_callback(self, func):
        self._on_error_callback = func

    @property
    def on_disconnect_callback(self):
        return self._on_disconnect_callback

    @on_disconnect_callback.setter
    def on_disconnect_callback(self, func):
        self._on_disconnect_callback = func

    @property
    def on_connect_callback(self):
        return self._on_connect_callback

    @on_connect_callback.setter
    def on_connect_callback(self, func):
        self._on_connect_callback = func

    @property
    def on_message_callback(self):
        return self._on_message_callback

    @on_message_callback.setter
    def on_message_callback(self, func):
        self._on_message_callback = func

    def __logger(self, msg, lvl=0):
        if self._on_log_callback is not None:
            self._on_log_callback(msg)

    def __error(self, user_data, error_str, error_code):
        if self._on_error_callback is not None:
            self._on_error_callback(user_data=user_data, error_str=error_str, error_code=error_code)

    ''' def __write_to_file(self, file_location, content):

        flags = os.O_WRONLY | os.O_CREAT
        try:
            with os.fdopen(os.open(file_location, flags, 0o600), 'w') as file_content:
                file_content.write(content)

                if self.on_message_callback is not None:
                    self.on_message_callback("Client is successfully provisioned.")

        except IOError as e:
            return e.errno '''

    def _close_connection(self):
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

    def _set_user_data(self, user_data):
        self.mqtt_client.user_data_set(user_data)
        self.user_data = user_data

    def _publish_api(self, publish_topic, subscribe_topic=None, error_topic=None, msg=None, callback=None,):

            if subscribe_topic is not None:
                self.mqtt_client.subscribe(subscribe_topic, 1)
            if error_topic is not None:
                self.mqtt_client.subscribe(error_topic, 1)

            self.mqtt_client.publish(publish_topic, msg, qos=1)

    def _provision(self, publish_topic, subscribe_topic=None, error_topic=None, msg=None, callback=None):
        self.provision_params = _ProvisionParams(publish_topic, subscribe_topic, error_topic, msg, callback)

    def _connect_api(self, port, cert_path=None, key_path=None, callback=None):


        self.__logger("INFO: Checking if the TLS is already set.")
        if self.mqtt_client._ssl_context is None:
            try:
                self.__logger("INFO: Setting TLS.")
                try:
                    self.mqtt_client.tls_set(self.connection_params.ca_path, certfile=cert_path,
                                                 keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED,
                                                 tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
                except ValueError:
                    self.__logger("ERROR: Could not set TLS.")
                    self.__error(self.user_data, "ERROR: Could not set TLS.", TVCMI_TLS_Error)
            except KeyboardInterrupt:
                return
            except IOError:
                err_msg = "Error occurred when setting TLS."
                self.__logger(err_msg)
                raise TLSError()

            except ValueError as e:
                self.__logger("ERROR: Error occurred when setting TLS." + e.message)
                raise TLSError(e.message)

        try:
            self.__logger("INFO: Trying to connect to MQTT and start the loop.")
            self.mqtt_client.connect_async(self.connection_params.host, port, keepalive=60, bind_address="")
        except gaierror:
            raise ConnectionParamError()
        except ValueError:
            raise ConnectionParamError()

        self.mqtt_client.loop_start()

        self.__logger("SUCCESS: MQTT loop started.")

    def _disconnect_api(self):
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()

    def on_connect(self, client, user_data, flags, rc):
        if rc is 0:
            self.connected = False
        try:

            if self.provision_params is not None and rc is 0:
                self.__logger("INFO: Publishing the certificate request for authorization.")
                self._publish_api(self.provision_params.publish_topic, self.provision_params.subscribe_topic,
                                   self.provision_params.error_topic, self.provision_params.msg,
                                   self.provision_params.callback)
            elif self.provision_params is not None and rc is not 0:
                err_msg = "ERROR: Could not authorize because the connection returned " + paho.connack_string(rc)
                self.__logger(err_msg)
                self.__error(user_data=user_data, error_str=err_msg, error_code=rc)
            elif self.provision_params is None and rc is 0:
                self.__logger("SUCCESS: Established a secture connection.")

                if self.on_connect_callback is not None:
                    self.on_connect_callback(user_data=user_data, error_str=paho.connack_string(rc), error_code=rc)
            else:
                err_msg = "ERROR: Could not connect. The connection returned " + paho.connack_string(rc)
                self.__logger(err_msg)
                self.__error(user_data=user_data, error_str=err_msg, error_code=rc)

        except TypeError:
            err_msg = "The arguments of on_api_connect do not match the required definition."
            self.__error(user_data=user_data, error_str=err_msg, error_code=TVCMI_Callback_ArgumentsMismatch)

        except KeyError:
            pass
        

    def on_message(self, client, user_data, msg):

        if "/certBack" in msg.topic:

            file_location = self.connection_params.cert_path
            self.__logger("Certback payload: " + msg.payload.decode('ISO-8859-1'))
            responses = re.findall('(-----BEGIN .+?-----(?s).+?-----END .+?-----)', msg.payload.decode('ISO-8859-1'))
            
            if len(responses) == 0:
                self.__logger("ERROR: Error in certificate response (certBack) ")
                return
                
            content = responses[0]
            self.__logger("Certifcate after  extract " + content)

            flags = os.O_WRONLY | os.O_CREAT
            try:
                with os.fdopen(os.open(file_location, flags, 0o600), 'wb+') as file_content:
                    file_content.write(content.encode())

                    if self.on_message_callback is not None:
                        self.on_message_callback(user_data=user_data, msg="Client is successfully provisioned.",
                                                 error_code=0)

            except IOError as e:
                self.__error(user_data=user_data, error_str="Error writing the certificate to file.",
                             error_code=e.errno)
        elif "/error" in msg.topic:
                error_info = json.loads(msg.payload.decode('utf-8'))
                self.__error(user_data=user_data, error_str=error_info['errorMessage'],
                             error_code=error_info['errorcode'])
        else:

            if self.on_message_callback is not None:
                self.on_message_callback(user_data=user_data, msg=msg.payload, error_code=0)

    def on_disconnect(self, client, user_data, rc):
        if rc is 0:
            self.connected = False
            self.__logger("INFO: Client disconnected.")
            if self._on_disconnect_callback is not None:
                self._on_disconnect_callback(user_data=user_data,
                                             error_str="Client successfully disconnected.",
                                             error_code=0)
        else:
            err_msg = "ERROR: Could not disconnect the client. Error code: " + str(rc)
            self.__logger(err_msg)
            self.__error(user_data=user_data, error_str=err_msg, error_code=rc)

    def on_log(self, client, userdata, level, buf):
        self.__logger(buf)

    
    def _subscribe_topic(self, subscribe_topic):
        self.mqtt_client.subscribe(subscribe_topic)

