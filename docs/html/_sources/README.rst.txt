TeamViewer IoT SDK for Python
##############################

This documentation describes the use of TeamViewer IoT SDK for connecting and pushing data to TeamViewer 
IoT Agent using python. 

- `Getting started`_
-  `Use the SDK`_
    - Client_
        - Constructor_
        - `Provisioning / Deprovisioning`_
        - `Connecting / Disconnecting`_
        - `Preparing data for publishing`_
            - Sensor_
            - Metric_
        - `Pushing data to TeamViewer IoT Agent`_
        - Callbacks_

-  License_
-  Support_


.. _Getting_started:

Getting started
===============

Requirements
------------

1: Python version >= 3.0

To check your Python version please run the following command:

.. code-block:: sh

    python --version


2: `TV IoT Agent up and running`_

.. _`TV IoT Agent up and running`: https://community.teamviewer.com/t5/TeamViewer-IoT-Knowledge-Base/Install-TeamViewer-IoT-Agent/ta-p/17084


3: Some of these libs can be asked to install:

    | sudo apt-get update
    | sudo apt-get install python3-pip
    | sudo apt-get install unzip
    | sudo apt-get install python3-setuptools
    | pip install --upgrade setuptools
    | sudo apt-get install libffi-dev
    | sudo apt-get install libssl-dev

Step 1
------
Download Python SDK from S3

.. code-block:: sh

    wget http://download.teamviewer-iot.com/sdks/python/v1.0.1/teamviewer_iot_python_sdk-1.0.1-py3-none-any.whl

Step 2
------
Install SDK

.. code-block:: sh

    pip3 install  teamviewer_iot_python_sdk-1.0.1-py3-none-any.whl

Step 3
------
Unzip package if you want to check docs and examples:

.. code-block:: sh

    unzip teamviewer_iot_python_sdk-1.0.1-py3-none-any.whl -d teamviewer_iot_python_sdk
    cd teamviewer_iot_python_sdk
    python3 ./examples/create_metric.py

Find examples and docs under the extracted folder.



.. _Use_the_SDK:

Use the SDK
===========

Client
------
The client is the main class used to establish an asynchronous connection to push data to TeamViewer IoT Agent. 

.. _Constructor:

Constructor
-----------

TVCMI_client()
""""""""""""""

.. code-block:: python

    TVCMI_client(parameters, user_data)

The constructor takes the following arguments: 

**- parameters**

Can either be a JSON or a config file. For both of the options the following fields must be initialized. 

| **MqttHost** - *The host name*. *As of now only 'localhost' is supported*.
| **MqttProvisionPort** - *Insecure port for certificate exchange*.
| **MqttPort** - *Secure port for establishing a TLS connection*.
| **MqttKeepAlive** - *Currently ignored*
| **CaFile** - *CA provided by TeamViewer Iot Agent*. *The default location is: /var/lib/teamviewer-iot-agent/certs/TeamViewerAuthority.crt*
| **CertFolder** - *Folder where the certificate signing request, private key and authorized certificates will be stored*.

| 
| Example of a config file: 


.. code-block:: python

    MqttHost             localhost
    MqttProvisionPort    18883
    MqttPort             18884
    MqttKeepAlive        60
    CaFile               /var/lib/teamviewer-iot-agent/certs/TeamViewerAuthority.crt
    CertFolder           /home/pi/Downloads/certs


**- user_data**

User defined data that will be passed to the user through the callbacks functions.

**Example:**

.. code-block:: python

    import TeamViewerIoTPythonSDK.TVCMI_client as TVCMI_client
    import TeamViewerIoTPythonSDK.TVCMI_error as Error
    import time
    import json
    import os.path

    # Obtaining the path of the file
    dir_path = os.path.abspath(os.path.dirname(__file__))
    # Choosing the location for the folder that stores the key and certificate
    cert_path = os.path.join(dir_path, "../certs")

    # putting connection parameters in JSON
    connection_parameters = {}
    connection_parameters['MqttHost'] = 'localhost'
    connection_parameters['MqttProvisionPort'] = '18883'
    connection_parameters['MqttPort'] = '18884'
    connection_parameters['MqttKeepAlive'] = 'None'
    connection_parameters['CaFile'] = '/var/lib/teamviewer-iot-agent/certs/TeamViewerAuthority.crt'
    connection_parameters['CertFolder'] = cert_path
    connector_params = json.dumps(connection_parameters)

    # Creating a new client to connect to TeamViewer IoT Agent
    client = TVCMI_client(connector_params)

set_user_data()
""""""""""""""""""""""""
.. code-block:: python

    set_user_data(user_data)

If user_data is not set when initializing the constructor, it can be set later through set_user_data function. 
The function takes the following arguments.

**- user_data**

User defined data that will be passed to the user through all the callbacks functions.


.. _Provisioning_/_Deprovisioning:

Provisioning / Deprovisioning
-----------------------------

provision()
"""""""""""

.. code-block:: python

    client.provision()

Checks for a private key and an authorized certificate in the CertFolder location passed to the
constructor. If key and certificate are not found in the folder, this function call will create a private key, 
certificate signing request and will insecurely connect to TeamViewer IoT Agent to obtain an authorized certificate. 
You must wait until the callback function is called to make sure the function finished its execution 
successfully.


**- Callbacks**


    `on_api_response()`_

    | Success message: "Client is successfully provisioned."
    | Success message: "Client is already provisioned."
    |
    | `on_api_error()`_
    | Error message: "Error writing the certificate to file."
    | Error code: IOError.errno
    |
    | `on_api_log()`_
    | Message: Log messages generated during execution. 


**Example:**

.. code-block:: python

    # Callback to be called when authorized certificate on provisioning is received
    def on_certificate_received(**kwargs):
        # Obtaining the response message
        message = kwargs.get('msg')

    # Setting a callback to receive an authorized certificate if the client is not provisioned
    client.on_api_response = on_certificate_received
    # Setting a callback for errors
    client.on_api_error = on_error

    # Provisioning the client
    client.provision()

    while True:
        time.sleep(1)


deprovision()
"""""""""""""

.. code-block:: python

    client.deprovision()

Deprovisions the client and deletes all the data associated with it. After this step no updates 
can be made to the client. 


.. _Connecting_/_Disconnecting:

Connecting / Disconnecting
--------------------------

connect_api()
"""""""""""""

.. code-block:: python

    client.connect_api()

Establishes a secure connection with TeamViewer IoT Agent. Must be called after the client 
is provisioned.


**- Callbacks**

    `on_api_connect()`_

**Example:**

.. code-block:: python

    import TeamViewerIoTPythonSDK.TVCMI_client as TVCMI_client
    import time

    # Callback to be called when connecting securely
    def on_connect(**kwargs):
        print("Secure connection is established.")
        # Setting the flag
        global secure_connection_established
        secure_connection_established = True

    # Flags to wait for API response
    secure_connection_established = False

    # Setting the callback to know when connected
    client.on_api_connect = on_connect

    # Establishing a secure connection with TeamViewer IoT Agent
    client.connect_api()

    # Waiting to connect securely
    while secure_connection_established is False:
        time.sleep(1)


disconnect_api()
""""""""""""""""

.. code-block:: python

    client.disconnect_api()

Disconnects the client.


**- Callbacks**

    `on_api_disconnect()`_

check_connection()
""""""""""""""""""

.. code-block:: python

    client.check_connection()

Checks if the connection with TeamViewer IoT Agent is alive. 


**- Callbacks**

    `on_api_response()`_

    Message: {"request": "Ping"}


.. _Preparing_data_for_publishing:

Preparing data for publishing
-----------------------------

Before the data can be published to TeamViewer IoT Agent, it needs to be formated according to
the data model used by `TeamViewer IoT Agent`_ . Sensor and metric must be created to
respectively group and describe the data pushed to TeamViewer IoT Agent.

Sensor
-------

Sensor is a logical unit that allows to group one or more metrics for pushing data to 
TeamViewer IoT. It is recommended to update all metrics that belong to the same sensor 
simultaneously to ensure that the data arrives with the same timestamp, so that it is 
better processed by rule engines.

create_sensor()
"""""""""""""""

.. code-block:: python

    client.create_sensor(sensor_name)

Creates a sensor with the passed name. You must wait for the callback to obtain and save the sensor ID. 
The sensor ID will be used to later identify the sensor. The parameters for the function are:

**- sensor_name**

The name of the sensor.
 


**- Callbacks**

    `on_api_response()`_

    Message: {"name": "SensorName", " sensorId":"d4170d999b9240a5863df622aad9fc4a"}

**Example:**

.. code-block:: python

    import TeamViewerIoTPythonSDK.TVCMI_client as TVCMI_client
    import time

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
        # Setting the flag
        global sensor_created
        sensor_created = True


    sensor_created = False
    # Setting the callback to receive the sensor ID
    client.on_api_response = on_sensor_created
    # Create a sensor
    client.create_sensor("sensor_name")

    # Waiting for create sensor to finish
    while sensor_created is False:
        time.sleep(1)


update_sensor_description()
"""""""""""""""""""""""""""

.. code-block:: python

    client.update_sensor_description(sensor_id, sensor_name)

Updates the description of the sensor. The function parameters are: 

**- sensor_id**

The sensor ID obtained when creating the sensor. 

**- sensor_name**

The name of the sensor.


**- Callbacks**

    `on_api_response()`_

    | Success message: {"Datasource Changed"}



list_sensors()
""""""""""""""

.. code-block:: python

    client.list_sensors()

Returns a JSON object listing the metadata of all registered sensors and their metric IDs 
of the specific client through the message field of the callback function .


**- Callbacks**

    `on_api_response()`_

    Example message: 

    .. code-block:: python

        [
        {
            "metrics" : [
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/0cbe4587c32644e0bf84180bf919cc51/inventory",
                    "metricId" : "0cbe4587c32644e0bf84180bf919cc51"
                },
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/639847246b5d45b8b759d01035c0b0a9/inventory",
                    "metricId" : "639847246b5d45b8b759d01035c0b0a9"
                },
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/7583b1d004604b18b9f7afd934a0528c/inventory",
                    "metricId" : "7583b1d004604b18b9f7afd934a0528c"
                },
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/7a75dfa08e014319828dac57e7f65c66/inventory",
                    "metricId" : "7a75dfa08e014319828dac57e7f65c66"
                },
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/b41e4458b7254419aaa079af07447d34/inventory",
                    "metricId" : "b41e4458b7254419aaa079af07447d34"
                },
                {
                    "link" : "/v1.0/c7721a37a2224a0bae22b8ef38e4de80/sensor/6b7b3daad85a41f4bb69a942233b06ae/metric/e3234e29aa1142c28b9e5e4b7b7cef4e/inventory",
                    "metricId" : "e3234e29aa1142c28b9e5e4b7b7cef4e"
                }
            ],
            "name" : "unispeed6",
            "sensorId" : "6b7b3daad85a41f4bb69a942233b06ae",
            "store" : true
        }
        ]

delete_sensor(sensor_id)
""""""""""""""""""""""""

.. code-block:: python

    client.delete_sensor()

Deletes the sensor and all the data associated with it. After this action no updates can be made
to the sensor. The function parameters are:

**- sensor_id**

The sensor ID obtained when creating the sensor. 


**- Callbacks** 

    `on_api_response()`_
    Message: {"Sensor was deleted"}


Metric
------

Metric is the container of the actual value which is pushed to TeamViewer IoT. 
Metrics must belong to a sensor and can’t exist independently. 

create_metric()

.. code-block:: python

    client.create_metric(metric_def, sensor_id)


Creates a metric describing the data to be published to TeamViewer IoT Agent. You must wait 
for the callback to obtain and save the metric ID. 
The metric ID will be used to later identify the metric. One or more metrics can be created
simultaneously. The parameters for the function are:

**- metric_def**

The message definition must contain the necessary metadata for the metrics in JSON format, 
which can be defined in two ways:

*Definition over predefined units of values:*

When defining a metric with a unit of value that is already defined in the valueUnit table 
below, the following fields must be present in the JSON message: matchingId, valueUnit, and 
the name of the metric.

*Definition over custom defined unit of values:*

When defining a metric with a custom unit of value, the following fields must be present in 
the JSON message: matchingId, valueType, name and valueAnnotation. This way of defining a 
metric gives a complete flexibility in what kind of data you want to push to TeamViewer IoT.

*metrics:* Array - Lists the definitions of all metric objects to be registered.

*matchingId:* String - Used to match the ID-s with metrics.

*name:* String - Name of the metric.

*valueUnit:* String	- Definition of the unit of value of the metric. Predefined valid units are:

| SI.ElectricCurrent.AMPERE
| SI.DataAmount.BIT
| SI.Temperature.CELSIUS
| SI.ElectricCapacitance.FARAD
| SI.Mass.GRAM
| SI.Frequency.HERTZ
| SI_Energy_JOULE
| SI.Length.METER
| SI.Velocity.METERS_PER_SECOND
| SI.AmountOfSubstance.MOLE
| SI.Force.NEWTON
| SI.ElectricResistance.OHM
| SI.Pressure.PASCAL
| SI.Angle.RADIAN
| SI.Duration.SECOND
| SI.Area.SQUARE_METRE
| SI.ElectricPotential.VOLT
| SI.Power.WATT
| SI.LuminousIntensity.CANDELA
| SI.Acceleration.METERS_PER_SQUARE_SECOND
| NoSI.Dimensionless.PERCENT
| NoSI.Dimensionless.DECIBEL

*valueAnnotation:* String - Optional field to define a custom unit for metric values.

*valueType:* String	- Defines the type of the custom defined unit. Valid entries are:

| bool
| string
| double
| integer

**- sensor_id**

The sensor ID obtained when creating the sensor. 


**- Callbacks** 

    `on_api_response()`_

Example message: 

**Example:**

.. code-block:: python

    import TeamViewerIoTPythonSDK.TVCMI_client as TVCMI_client
    import time
    import json

    # Callback to be called when metric is created
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
        # Setting the flag
        global metrics_created
        metrics_created = True
        
    metrics_created = False

    # Setting the callback to receive the sensor ID
    client.on_api_response = on_metric_created

    # Defining metric 1
    metric1_parameters = {}
    metric1_parameters['matchingId'] = 1
    metric1_parameters['name'] = 'metric1_name'
    metric1_parameters['valueAnnotation'] = 'your_value_unit_for_metric1'
    metric1_parameters['valueType'] = 'string'

    metric1_json = json.dumps(metric1_parameters)

    # Defining metric 2
    metric2_parameters = {}
    metric2_parameters['matchingId'] = 2
    metric2_parameters['name'] = 'metric2_name'
    metric2_parameters['valueAnnotation'] = 'your_value_unit_for_metric2'
    metric2_parameters['valueType'] = 'integer'

    metric2_json = json.dumps(metric2_parameters)

    # putting metric 1 and metric 2 into a single container
    metrics_container = {}
    metrics_container['metrics']= [metric1_json, metric2_json]

    metrics_container_json = json.dumps(metrics_container)

    # Create a metric
    client.create_metric(metrics_container_json, sensor_id)

    # Waiting for create metric to finish
    while metrics_created is False:
        time.sleep(1)


describe_metric()

.. code-block:: python

    client.describe_metric(metric_id, sensor_id)


Returns through the callback function a JSON object containing the metadata definition of the 
registered metric whose ID is passed to the function. This metric must belong to 
the sensor whose ID is also passed to the function. 

**- metric_id**

The metric ID obtained when creating the metric. 

**- sensor_id**

The sensor ID obtained when creating the sensor. 


delete_metric()

.. code-block:: python

    client.delete_metric(msg, sensor_id)

Deletes the metrics whose IDs are passed to the function as a JSON. All metrics being deleted must 
belong to the same sensor whose ID is passed in the function as well. After deletion no updates are possible 
to the deleted metrics.

**- msg**

JSON containing metric IDs to be deleted. 

    **Example**

    .. code-block:: python

        "{\"metrics\": [{\"metricId\" : \"94c2c5e193bb437195368c08f0bd86ab\" },
         {\"metricId\" : \"94c2c5e193bb437195368c08f0bd86ac\" }] }"

**- sensor_id**

The sensor ID obtained when creating the sensor. 


.. _Pushing_data_to_TeamViewer_IoT_Agent:

Pushing data to TeamViewer IoT Agent
------------------------------------

push_metrics()

.. code-block:: python

    client.push_metrics(sensor_id, metric_data, timestamp)

Puts metric data in TeamViewer IoT Agent. 

**- sensor_id**

The sensor ID obtained when creating the sensor. 

**- metric_data**

JSON containing metric values.

**- timestamp**

| Time the data is sent for.
| Optional parameter, data is displayed for realtime if the timestamp parameter is missing.

    **Example**

    .. code-block:: python

        "{ \"metrics\": [ {\"value\" : 21.5, \"metricId\" : \"94c2c5e193bb437195368c08f0bd86ab\" }, 
        {\"value\" : 21.5, \"metricId\" : \"94c2c5e193bb437195368c08f0bd86ac\" } ], \"timestamp\" : 1531736501248 }"



.. _Callbacks:

Callbacks
---------
Since the client establishes an asynchronous connection, callbacks need to be initialized for each method to receive 
responses from TeamViewer IoT Agent.

`on_api_connect()`_
"""""""""""""""""""

.. code-block:: python

    on_api_connect(user_data, error_str, error_code)


Called when a connection with TeamViewer IoT Agent is established. 

**- user_data**

User defined data that will be passed to the user through the callbacks functions.

**- error_str**

MQTT error string describing the state of the connection. 

| 0: Connection successful 
| 1: Connection refused - incorrect protocol version 
| 2: Connection refused - invalid client identifier 
| 3: Connection refused - server unavailable 
| 4: Connection refused - bad username or password 
| 5: Connection refused - not authorized 6-255: Currently unused.

**- error_code**

MQTT error codes describing the state of the connection. 

| 0: Connection successful 
| 1: Connection refused - incorrect protocol version 
| 2: Connection refused - invalid client identifier 
| 3: Connection refused - server unavailable 
| 4: Connection refused - bad username or password 
| 5: Connection refused - not authorized 6-255: Currently unused.

**Example**

.. code-block:: python

    # Callback to be called when connecting securely
    def on_connect(**kwargs):
        print("Secure connection is established.")
        # Setting the flag
        global secure_connection_established
        secure_connection_established = True

    # Setting the callback to know when connected
    client.on_api_connect = on_connect


`on_api_response()`_
""""""""""""""""""""

.. code-block:: python

    on_api_response(user_data, msg, error_code)

Called when a message from TeamViewer IoT Agent is received.

**- user_data**

User defined data that will be passed to the user through the callbacks functions.

**- msg**

Message received from TeamViewer IoT Agent.

**- error_code**

| 0: UnknownError
| 1: NoBackendConnection
| 2: NoLicence
| 3: InternalError
| 4: InvalidJson
| 5: JsonIsNotAObject
| 6: MissingParameter
| 7: ParameterIsNotAString
| 8: ParameterIsNotANumber
| 9: ParameterisNotABool
| 10: ParameterIsNotAnArray
| 11: ParameterIsNotAnInteger
| 12: UnknownValueUnit
| 13: UnknownMetricType
| 14: ValueUnitOrValueTypeHasToBeProvided
| 15: UnknownSensorId
| 16: UnknownMetricId
| 17: NoMetricsUpdated
| 18: ForbiddendAccess
| 19: OutOfRange


`on_api_disconnect()`_
""""""""""""""""""""""

.. code-block:: python

    on_api_disconnect(user_data, error_str, error_code)

Called when the client gets disconnected. Parameters are the same as that of on_api_connect().

`on_api_error()`_
"""""""""""""""""

.. code-block:: python

    on_api_error(user_data, error_str, error_code)

Called instead of initialized callback when TeamViewer IoT Agent replies with an error. 
To be called the callback must be initialized by the user. 
Parameters are the same as that of on_api_connect().

`on_api_log()`_
"""""""""""""""
.. code-block:: python

    on_api_log(msg)

Called on every log message while execution. Logging levels are not yet supported. 
Parameters are the same as that of on_api_connect().

License
=======

This SDK is distributed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

.. _License:

Support
=======

Bugs and issues can be reported through issues section at https://github.com/landreasyan/teamviewer-iot-client-sdk-python/issues.


