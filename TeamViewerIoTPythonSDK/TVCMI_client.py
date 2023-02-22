from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from .TVCMI_mqtt_client import _ConnectNetwork
from .TVCMI_Connection_Parameters import ConnectionParameters
from .TVCMI_error import FileError, ConfigError, InputError, KeyGenerationError, DirectoryError
from .TVCMI_config_reader import TvcmiConfigParser
from .TVCMI_CheckForCertificate import is_certificate_valid
import hashlib
import os
import json
from enum import Enum

class CertOverrideMode(Enum):
    OVERRIDE = 1
    NOT_OVERRIDE = 2
    SMART = 3


class TVCMI_client(object):
    version = "/v1.0/"

    def __init__(self, parameters, user_data=None):

        try:
            json_config = parameters
            self.json_config = json_config
            #json_config = json.loads(parameters)
            for key, data in json_config.items():
                try:
                    if isinstance(data, unicode):
                        json_config[key] = json_config[key].encode('utf-8')
                except NameError:
                        json_config[key] = json_config[key]

            self._connection_params = ConnectionParameters(json_config['CertFolder'], json_config["ClientName"], 
                                                            int(json_config['MqttPort']), int(json_config['MqttProvisionPort']),
                                                           json_config['MqttHost'], json_config['CaFile'], json_config['OverrideCerts'])
            self._connection_params.user_data = user_data
        except ValueError:
            try:
                self._connection_params = TvcmiConfigParser().parser(parameters)
            except FileError:
                raise ConfigError(parameters)

        except KeyError:
            raise InputError(parameters)

        self._mqtt_connection_insecure = _ConnectNetwork(self._connection_params)
        self._mqtt_connection = _ConnectNetwork(self._connection_params)
        self._on_api_connect = None
        self._on_api_response = None
        self._on_api_disconnect = None
        self._on_api_error = None
        self._on_api_log = None


# helper
    @property
    def on_api_connect(self):
        return self._on_api_connect

    @on_api_connect.setter
    def on_api_connect(self, func):
        self._on_api_connect = func
        self._mqtt_connection.on_connect_callback = func
        self._mqtt_connection_insecure.on_connect_callback = func

    @property
    def on_api_response(self):
        return self._on_api_response

    @on_api_response.setter
    def on_api_response(self, func):
        self._on_api_response = func
        self._mqtt_connection.on_message_callback = func
        self._mqtt_connection_insecure.on_message_callback = func

    @property
    def on_api_error(self):
        return self._on_api_error

    @on_api_error.setter
    def on_api_error(self, func):
        self._on_api_error = func
        self._mqtt_connection.on_error_callback = func
        self._mqtt_connection_insecure.on_error_callback = func

    @property
    def on_api_disconnect(self):
        return self._on_api_disconnect

    @on_api_disconnect.setter
    def on_api_disconnect(self, func):
        self._on_api_disconnect = func
        self._mqtt_connection.on_disconnect_callback = func
        self._mqtt_connection_insecure.on_disconnect_callback = func

    @property
    def on_api_log(self):
        return self._on_api_log

    @on_api_log.setter
    def on_api_log(self, func):
        self._on_api_log = func
        self._mqtt_connection.on_log_callback = func
        self._mqtt_connection_insecure.on_log_callback = func

    def __logger(self, msg, lvl=0):
        if self._on_api_log is not None:
            self._on_api_log(msg)


    def __write_to_file(self, file_path, file_content):

        self.__logger("INFO: Trying to write to {file}".format(file=file_path))
        flags = os.O_WRONLY | os.O_CREAT
        try:
            with os.fdopen(os.open(file_path, flags, 0o600), 'wb+') as open_file:
                open_file.write(file_content)
            return 0
        except (IOError, OSError, FileExistsError) as e:
            error_str = "ERROR: Error occurred while writing to {file}. I/O Error: {errno}: {error_str}".format(
                file=file_path, errno=e, error_str=os.strerror(e))
                
            error = FileError(file_path, error_str, e)
            self.__logger(error_str)
            raise error
        self.__logger("SUCCESS: Writing to {file} was successful.".format(file=file_path))


    def __remove_file_if_exists(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            self.__logger("INFO: File removed {file}".format(file=file_path))
        else:
            self.__logger("INFO: Removing file, does not exist {file}".format(file=file_path))

    @staticmethod
    def __read_from_file(file_path):
        try:
            with open(file_path) as file_content:
                file_read = file_content.read()
            file_content.close()
            return file_read
        except IOError as e:
            raise FileError(file_path, os.strerror(e), e)

    def __get_cert_hash(self, cert_file):
        try:
            cert_hash = hashlib.sha256(cert_file.encode()).hexdigest()
        except AttributeError:
            cert_hash = hashlib.sha256(cert_file).hexdigest()
        self.__logger("SUCCESS: Finished calculated the hash value of the certificate request")
        return cert_hash

    def __get_connector_id(self, connector_id=None, cert=None):
        
        if connector_id is not None:
            return connector_id
        elif connector_id is None and cert is None:
            try:
                cert_file = self.__read_from_file(self._connection_params.cert_path).encode()
            except AttributeError:
                cert_file = self.__read_from_file(self._connection_params.cert_path)
            cert_file_pem = x509.load_pem_x509_certificate(cert_file, default_backend())
            connector_id = cert_file_pem.subject.get_attributes_for_oid(x509.OID_COMMON_NAME)[0].value

            return connector_id
       
    def __create_cert(self):
        certificate_request_builder = x509.CertificateSigningRequestBuilder()
        certificate_request_builder = certificate_request_builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'{}'.format(self._connection_params.client_name))]))
        certificate_request_builder = certificate_request_builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,)

        certificate_request = certificate_request_builder.sign(self._connection_params.key, hashes.SHA256(), default_backend())

        csr_file = certificate_request.public_bytes(serialization.Encoding.PEM)

        self.__write_to_file(self._connection_params.csr_path, csr_file)

        self.__logger("SUCCESS: Certificate signing request is created.")
        return csr_file

    def __create_private_key(self):
        try:

            self._connection_params.key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
        except x509.exceptions.UnsupportedAlgorithm:
            error = KeyGenerationError()
            self.__logger("ERROR: Error occurred while creating the private key." + error.message)

            raise error

        self._connection_params.key_str = self._connection_params.key.private_bytes(
                encoding=serialization.Encoding.PEM, 
                format=serialization.PrivateFormat.TraditionalOpenSSL, 
                encryption_algorithm=serialization.NoEncryption())

        self.__write_to_file(self._connection_params.key_path, self._connection_params.key_str)

        self.__logger("SUCCESS: Private key created.")
        return self._connection_params.key_str

    def __check_for_certificate(self):
        self.__logger("INFO: Checking if {cert} cert and {key} key exsit.".format(cert=self._connection_params.cert_path, key=self._connection_params.key_path))
        if not os.path.isfile(self._connection_params.cert_path) or not os.path.isfile(
                              self._connection_params.key_path):
            self.__logger("INFO: Client is not provisioned.")
            return False
        else:
            self.__logger("INFO: Client is provisioned.")
            return True

    def __check_or_create_directory(self):
        if not os.path.exists(self._connection_params.directory):
            try:

                self.__logger("INFO: The passed directory of certificates does not exist.")
                self.__logger("INFO: Trying to create the directory.")
                os.makedirs(self._connection_params.directory)
            except OSError as e:
                if not os.path.isdir(self._connection_params.directory):
                    self.__logger("ERROR: Error occurred while creating {dir} to hold certificates: I/O Error {errno}:"
                                  "{error_string}".format(dir=self._connection_params.directory, errno=e,
                                                          error_string=os.strerror(e)))

                    raise DirectoryError(self._connection_params. directory, os.strerror(e), e)

        self.__logger("INFO: Check for {directory} successfully passed.".format(directory=
                                                                                self._connection_params.directory))

# connector
    def set_user_data(self, user_data):
        self._connection_params.user_data = user_data
        if self._mqtt_connection is not None:
            self._mqtt_connection._set_user_data(user_data)
        if self._mqtt_connection_insecure is not None:
            self._mqtt_connection_insecure._set_user_data(user_data)

    def connect_api(self):

        self._mqtt_connection_insecure._close_connection()
        if self._mqtt_connection.mqtt_client is None:
            self._mqtt_connection._create_mqtt_client(self._connection_params.user_data)

        self.__logger("INFO: Trying to connect the client.")
        self._mqtt_connection._connect_api(self._connection_params.port, self._connection_params.cert_path,
                                           self._connection_params.key_path, self.on_api_connect)

    def disconnect_api(self):
        self.__logger("INFO: Trying to disconnect the client.")
        self._mqtt_connection._disconnect_api()

    def provision(self):
        self.__logger("INFO: Checking if {directory} exists.".format(directory=self._connection_params.directory))
        self.__check_or_create_directory()
        self.__logger("Certificate override mode " + str(CertOverrideMode.OVERRIDE))
        if self._connection_params.override_certs == CertOverrideMode.OVERRIDE:
            self.__logger("INFO: removing exisiting certs")
            self.removing_certificates()
        elif self.__check_for_certificate() and self._connection_params.override_certs == CertOverrideMode.SMART:
            self.__logger("Starting provision on certificate override mode = SMART")
            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.__logger("Running script for checking expire dates")
            #Call here check certificate bash script
            self.__logger("Checking for certificate validation")
            is_cert_valid = is_certificate_valid(self.json_config)
            if not is_cert_valid:
                self.__logger("Removing invalid certificates")
                self.removing_certificates()          


        self.__logger("INFO: Checking if client is already provisioned.")
        if not self.__check_for_certificate():
            self.__logger("INFO: Trying to create a private key.")
            self.__create_private_key()
            self.__logger("INFO: Trying to create a certificate request.")
            self._connection_params.csr = self.__create_cert()
            self.__logger("INFO: Trying to calculate the hash value of the certificate request.")
            cert_hash = self.__get_cert_hash(self._connection_params.csr)

            self.__logger("INFO: Trying to connect to the API insecurely.")
            self._mqtt_connection_insecure._create_mqtt_client(self._connection_params.user_data)
            self._mqtt_connection_insecure.on_log_callback = self._on_api_log
            self._mqtt_connection_insecure.on_error_callback = self._on_api_error
            self._mqtt_connection_insecure.on_disconnect_callback = self._on_api_disconnect
            self.__logger("INFO: Trying to establish insecure connection.")
            self._mqtt_connection_insecure._connect_api(self._connection_params.port_insecure, None, None,
                                                         self.on_api_connect)

            base = '/certBack/' + cert_hash
            publish_topic = '/createConnector'
            subscribe_topic = base
            error_topic = base + '/error'

            msg = self._connection_params.csr

            self._mqtt_connection_insecure._provision(publish_topic, subscribe_topic, error_topic, msg,
                                                       self.on_api_response)
        else:
            self.__logger("INFO: Client is already provisioned.")
            self.on_api_response(user_data=self._connection_params.user_data, msg="Client is already provisioned.",
                                 error_code=1)


    def removing_certificates(self):
        self.__remove_file_if_exists(self._connection_params.key_path)
        self.__remove_file_if_exists(self._connection_params.cert_path)
        self.__remove_file_if_exists(self._connection_params.csr_path)
        self.__remove_file_if_exists(self._connection_params.key_der_path)
        self.__remove_file_if_exists(self._connection_params.cert_der_path)


    def list_sensors(self):
    
        connector_id = self.__get_connector_id()
        
        base = self.version + connector_id + '/inventory'

        publish_topic = base 
        subscribe_topic = base + '/inbox'
        error_topic = base + '/error/inbox'
        
        msg = '{}'
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

    def get_connector_id(self):

        return self.__get_connector_id()

    def deprovision(self):
        
        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/delete'
        publish_topic = base 
        error_topic = base + '/error/inbox'

        msg = '{}'
        self.__logger("INFO: Publishing client deprovisioning request to the API.")
        self._mqtt_connection._publish_api(publish_topic, None, error_topic, msg, self.on_api_error)
    
    def check_connection(self):
        self.__logger("INFO: Checking if the connection is alive.")
        self.__logger("INFO: Getting the client ID")
        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/ping'
        publish_topic = base
        subscribe_topic = base + '/info/inbox'
        error_topic = base + '/error/inbox'

        msg = '{"request": "Ping"}'

        self.__logger("INFO: Publishing check connection request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)
      
#sensor
    def create_sensor(self, sensor_name):
        self.__logger("INFO: Creating a sensor.")
        self.__logger("INFO: Getting the client ID.")
        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/sensor'
        publish_topic = base + '/create'
        subscribe_topic = base + '/inbox'
        error_topic = base + '/error/inbox'

        msg = '{{"name" : "{name}"}}'.format(name=sensor_name)

        self.__logger("INFO: Publishing create sensor request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

    def push_metrics(self, sensor_id, metric_data, timestamp=None):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id +'/sensor/'+ sensor_id

        publish_topic = base +"/metric/pushValues"
        subscribe_topic = base + '/info/inbox'
        error_topic = base + '/error/inbox'

        if timestamp is not None:
            metric_data["timestamp"] = timestamp
        msg = json.dumps(metric_data)
        self.__logger("INFO: Publishing sensor update request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

    def update_sensor_description(self, sensor_id, sensor_metadata):

        connector_id = self.__get_connector_id()
    
        base = self.version + connector_id +'/sensor/'+ sensor_id + '/update'

        publish_topic = base 
        #subscribe_topic = base + '/info/inbox'
        error_topic = base + '/error/inbox' 

        msg = '{{"name" : "{sensor_name}"}}'.format(sensor_name=sensor_metadata)

        self.__logger("INFO: Publishing sensor metadata update request to the API.")
        self._mqtt_connection._publish_api(publish_topic, None, error_topic, msg, self.on_api_response)

    def update_metrics(self, sensor_id, metric_info):
        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/sensor/' + sensor_id + '/metric/update'

        publish_topic = base
        subscribe_topic = base + '/info/inbox'
        error_topic = base + '/error/inbox'

        msg = json.dumps(metric_info)

        self.__logger("INFO: Publishing sensor metrics metadata update request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic , error_topic, msg, self.on_api_response)

    def describe_metric(self, metric_id, sensor_id):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/sensor/' + sensor_id + '/metric/' + metric_id +'/inventory'

        publish_topic = base 
        subscribe_topic = base + '/inbox'
        error_topic = self.version + connector_id + '/sensor/' + sensor_id + '/inventory/error/inbox'

        msg = '{}'

        self.__logger("INFO: Publishing describe metric request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)
    
    def delete_sensor(self, sensor_id):

        connector_id = self.__get_connector_id()
    
        base = self.version + connector_id + '/sensor/' + sensor_id + '/delete'
        publish_topic = base
        subscribe_topic = base + '/info/inbox'
        error_topic = base + '/error/inbox'

        msg = '{}'
        self.__logger("INFO: Publishing delete sensor request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

# metric
    def create_metric(self, metric_def, sensor_id):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/sensor/' + sensor_id + '/metric'

        publish_topic = base
        subscribe_topic = base + '/inbox'
        error_topic = base + '/error/inbox'

        msg = json.dumps(metric_def)
        self.__logger("INFO: Publishing create metric request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

    def delete_metric(self, msg, sensor_id):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/sensor/' + sensor_id
        
        publish_topic = base + '/metric/delete'
        subscribe_topic = base + '/delete/info/inbox'
        error_topic = base + '/delete/error/inbox'

        self.__logger("INFO: Publishing delete metric request to the API.")
        self._mqtt_connection._publish_api(publish_topic, subscribe_topic, error_topic, msg, self.on_api_response)

    def listen_live_data(self, sensor_id):
        connector_id = self.__get_connector_id()
        live_data_topic = self.version + connector_id +  "/sensor/" + sensor_id + "/livedata"
        self.__logger("INFO: Subscribing to live data")
        self._mqtt_connection._subscribe_topic(live_data_topic)

# error
    def client_error(self, error_message):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + '/error'
        
        publish_topic = base
        error_topic = base + '/inbox'

        msg = error_message

        self.__logger("INFO: Publishing client error request to the API.")
        self._mqtt_connection._publish_api(publish_topic, None, error_topic, msg, self.on_api_error)

    def sensor_error(self, error_message, sensor_id):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + 'sensor' + sensor_id + '/error'
        
        publish_topic = base
        error_topic = base + '/inbox'

        msg = error_message

        self.__logger("INFO: Publishing sensor error request to the API.")
        self._mqtt_connection._publish_api(publish_topic, None, error_topic, msg, self.on_api_error)

    def metric_error(self, error_message, metric_id, sensor_id):

        connector_id = self.__get_connector_id()

        base = self.version + connector_id + 'sensor' + sensor_id + 'metric' + metric_id + '/error'
        
        publish_topic = base
        error_topic = base + '/inbox'

        msg = error_message

        self.__logger("INFO: Publishing metric error request to the API.")
        self._mqtt_connection._publish_api(publish_topic, None, error_topic, msg, self.on_api_error)


    def read_cert_from_file(self):
        return self.__read_from_file(self._connection_params.cert_path)
    
    def read_key_from_file(self):
        return self.__read_from_file(self._connection_params.key_path)

    def read_ca_from_file(self):
        return self.__read_from_file(self._connection_params.ca_path)

    def get_cert_path(self):
        return self._connection_params.cert_path

    def get_key_path(self):
        return self._connection_params.key_path

    def get_ca_path(self):
        return self._connection_params.ca_path

    def get_cert_der_path(self):
        return self._connection_params.cert_der_path

    def get_key_der_path(self):
        return self._connection_params.key_der_path

    def get_ca_der_path(self):
        return self._connection_params.ca_der_path

