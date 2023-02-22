from setuptools import setup

setup(name='teamviewer_iot_mqtt_sdk',
      version='1.1.0',
      description='Iot client to put data in TeamViewer Iot.',
      url='',
      author='TeamViewer',
      author_email='iot-support@teamviewer-iot.com',
      license='MIT',
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
      packages=['TeamViewerIoTPythonSDK'],
      include_package_data=True,
      install_requires=[
          'setuptools>=18.5',
          'cryptography',
          'paho-mqtt==1.3.1'
      ],
      zip_safe=False)